from django.shortcuts import render
from django.views.generic import View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
# --------------------------------------------------------
from datetime import datetime, timedelta
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML

from django.db.models import Sum
from rebs_contract.models import Contract
from rebs_notice.models import SalesBillIssue
from rebs_cash.models import (SalesPriceByGT, ProjectCashBook,
                              InstallmentPaymentOrder, DownPayment)

TODAY = datetime.today().strftime('%Y-%m-%d')


class Dashboard(LoginRequiredMixin, TemplateView):
    template_name = 'rebs/main/1_1_dashboard.html'


def memu2_1(request):
    return render(request, 'rebs/main/2_1_schedule.html')


class PdfExportBill(View):
    """고지서 리스트"""

    def get(self, request):
        context = {}
        project = request.GET.get('project')
        context['issue_date'] = request.GET.get('date')
        context['bill'] = SalesBillIssue.objects.get(project_id=project)

        context['pay_orders'] = pay_orders = InstallmentPaymentOrder.objects.filter(project_id=project)
        now_due_order = context['bill'].now_payment_order.pay_code if context['bill'].now_payment_order else 2
        context['contractor_id'] = contractor_id = request.GET.get('seq').split('-')
        context['data_list'] = []

        for id in contractor_id:

            cont = {}
            cont['contract'] = contract = Contract.objects.get(contractor__id=id)  # 해당 계약건

            # 1. 차수/타입별/동호수별 분양가 및 계약금 + 중도금 + 잔금 구하기
            group = contract.order_group  # 차수
            type = contract.contractunit.unit_type  # 타입
            try:  # 동호수
                cont['unit'] = unit_set = contract.contractunit.unitnumber
            except Exception:
                cont['unit'] = unit_set = None
            # 해당 계약건 분양가 # this_price = '동호 지정 후 고지'
            this_price = contract.contractunit.unit_type.average_price
            prices = SalesPriceByGT.objects.filter(project_id=project, order_group=group, unit_type=type)
            if unit_set:
                floor = contract.contractunit.unitnumber.floor_type
                this_price = prices.get(unit_floor_type=floor).price
            cont['price'] = this_price
            # 계약금 구하기
            this_orders = InstallmentPaymentOrder.objects.filter(project=project)  # 해당 건 전체 약정 회차
            down_num = this_orders.filter(pay_sort='1').count()
            try:
                dp = DownPayment.objects.get(project_id=project, order_group=contract.order_group,
                                             unit_type=contract.contractunit.unit_type)
                cont['down'] = down = dp.payment_amount
            except:
                pn = round(down_num / 2)
                cont['down'] = down = int(this_price * 0.1 / pn)
            down_total = down * down_num

            # 중도금 구하기
            med_num = this_orders.filter(pay_sort='2').count()
            cont['medium'] = medium = int(this_price * 0.1)
            medium_total = medium * med_num

            # 잔금 구하기
            bal_num = this_orders.filter(pay_sort='3').count()
            cont['balance'] = balance = int((this_price - down_total - medium_total) / bal_num)
            # --------------------------------------------------------------

            # 2. 완납금액 및 완납회차 구하기
            paid_list = ProjectCashBook.objects.filter(is_contract_payment=True, contract=contract).order_by(
                'installment_order', 'deal_date')
            paid_sum = paid_list.aggregate(Sum('income'))['income__sum']  # 기 납부총액
            cont['paid_sum'] = paid_sum if paid_sum else 0  # 기 납부총액(None 이면 0)

            paid_order = 0  # 완납회차
            paid_order_amount = 0  # 완납회차까지 약정액 합계
            total_cont_amount = 0  # 지정회차까지 약정액 합계
            pm_cost_sum = 0  # pm 용역비 누계

            due_date_list = []  # 회차별 납부기한
            paid_date_list = []  # 회차별 최종 수납일자

            def_payment = 0  # 지연금 = 납부할 금액 - 납부한 금액
            dates_delay = 0  # 회차별 지연일수

            payment_list = []  # 회차별 납부금액
            def_pay_list = []
            delay_day_list = []  # 회차별 지연일수

            penalty_sum = 0 # 가산금 총액

            first_paid_date = None # 최초 계약금 완납일

            for to in this_orders:
                pay_amount = 0 # 납부할 금액
                if to.pay_sort == '1':
                    pay_amount = down
                if to.pay_sort == '2':
                    pay_amount = medium
                if to.pay_sort == '3':
                    pay_amount = balance

                total_cont_amount += pay_amount  # 지정회차까지 약정액(pay_amount) 합계 (total_cont_amount)
                if paid_sum >= total_cont_amount:  # 기 납부총액(paid_sum)이 약정액(total_cont_amount)보다 같거나 큰지 검사
                    paid_order = to.pay_code  # paid_order = 완납회차
                    paid_order_amount += pay_amount  # 완납회차까지 약정액(pay_amount) 누계(paid_order_amount)
                if to.is_pm_cost:
                    pm_cost_sum += pay_amount  # pm 용역비 누계

                now_payment = paid_list.filter(installment_order=to)
                paid_amount = now_payment.aggregate(Sum('income'))['income__sum']
                paid_date = now_payment.latest('deal_date').deal_date if now_payment else None
                if to.pay_code == 1:
                    first_paid_date = paid_date
                payment_list.append(paid_amount) # 회차별 납부금액
                paid_date_list.append(paid_date)  # 회차별 최종 수납일자

                def_payment = pay_amount - paid_amount  # 지연금 = 납부할 금액 - 납부한 금액
                def_pay_list.append(def_payment) # 지연금 리스트

                # 계약일과 최초 계약금 납부일 중 늦은 날을 기점으로 30일
                reference_date = first_paid_date if first_paid_date and (first_paid_date > contract.contractor.contract_date) else contract.contractor.contract_date

                if to.pay_time == 1 or to.pay_code == 1:  # 최초 계약금일 때
                    due_date = contract.contractor.contract_date  # 납부기한

                elif to.pay_time == 2 or to.pay_code == 2:  # 2차 계약금일 때
                    # acc_def_payment = def_payment + acc_def_payment # 지연금 누계
                    due_date = reference_date + timedelta(days=30)  # 납부기한 = 기준일 30일 후
                    if to.pay_due_date:  # 당회차 납부기한이 설정되어 있을 때 -> 계약후 30일 후와 설정일 중 늦은 날을 납부기한으로 한다.
                        due_date = due_date if due_date > to.pay_due_date else to.pay_due_date  # 납부기한

                    # 지연가산금 계산 로직 ---------------------------------------------------------------
                    second_payment = paid_list.filter(installment_order__lte=2)  # 당 회차까지 납부 데이터
                    now_pay = 0  # 당 회차까지 납부액 누계

                    for np in second_payment:  # 1 - 2회차 납부 데이터
                        now_pay += np.income  # 당회 납부액 누계

                        if now_pay < paid_order_amount and np.deal_date > due_date: # 납부 연체 시
                            delay = np.deal_date - due_date
                            dates_delay = delay.days  # 지연일수
                            penalty_sum += self.overdue_rate(def_payment, dates_delay)

                else:  # 3회차 이후 납부회차인 경우
                    # acc_def_payment = def_payment + acc_def_payment # 지연금 누계
                    if to.pay_due_date:
                        due_date = to.pay_due_date if to.pay_due_date > reference_date + timedelta(days=30) else reference_date + timedelta(days=30)  # 납부기한
                    else:
                        due_date = None

                    # 지연가산금 계산 로직 ---------------------------------------------------------------
                    other_payment = now_payment  # 당 회차까지 납부 데이터
                    now_pay = 0  # 당 회차까지 납부액 누계

                    for np in other_payment:  # 3회차 이상 납부 데이터
                        now_pay += np.income  # 당회 납부액 누계

                        if now_pay < paid_order_amount and np.deal_date > due_date:  # 납부 연체 시
                            delay = np.deal_date - due_date
                            dates_delay = delay.days  # 지연일수
                            penalty_sum += self.overdue_rate(def_payment, dates_delay)

                due_date_list.append(due_date)  # 회차별 납부일자
                delay_day_list.append(dates_delay)  # 회차별 지연일수

                if to.pay_code == now_due_order:  # 순회 회차가 지정회차와 같으면 순회중단
                    break

            cont['paid_orders'] = this_orders.filter(pay_code__lte=now_due_order)  # 지정회차까지 회차
            cont['due_date_list'] = list(reversed(due_date_list))  # 회차별 납부일자
            cont['paid_date_list'] = list(reversed(paid_date_list))  # 회차별 최종 수납일자
            cont['payment_list'] = list(reversed(payment_list))  # 회차별 납부금액
            cont['delay_day_list'] = list(reversed(delay_day_list))  # 회차별 지연일수
            cont['def_pay_list'] = list(reversed(def_pay_list)) # 회차별 지연금 리스트
            cont['penalty_sum'] = penalty_sum # 가산금 합계
            # --------------------------------------------------------------

            # 4. 미납 회차 (지정회차 - 완납회차)
            cont['second_date'] = contract.contractor.contract_date + timedelta(days=30)
            unpaid_orders_all = this_orders.filter(pay_code__gt=paid_order)  # 최종 기납부회차 이후 납부회차
            cont['unpaid_orders'] = unpaid_orders = unpaid_orders_all.filter(pay_code__lte=now_due_order)  # 최종 기납부회차 이후부터 납부지정회차 까지 회차그룹
            cont['unpaid_amounts_sum'] = unpaid_amounts_sum = total_cont_amount - paid_order_amount
            # --------------------------------------------------------------

            # 5. 미납 금액 (약정금액 - 납부금액)
            cont['total_cont_amount'] = total_cont_amount
            cont['cal_unpaid'] = cal_unpaid = paid_order_amount - paid_sum
            cont['cal_unpaid_sum'] = cal_unpaid_sum = total_cont_amount - paid_sum
            cont['arrears'] = 0  # 연체료 - 향후 연체료 계산 변수
            cont['arrears_sum'] = arrears_sum = 0  # 연체료 합계 - 향후 연체료 합계 계산 변수
            cont['pm_cost_sum'] = pm_cost_sum

            # 6. 잔여 약정 목록
            cont['remaining_orders'] = remaining_orders = this_orders.filter(pay_code__gt=now_due_order)
            if not unit_set:
                cont['remaining_orders'] = remaining_orders.filter(pay_sort='1')
            cont['modi_dates'] = 0  # 선납 or 지연 일수
            cont['modifi'] = 0  # 선납할인 or 연체 가산금계산
            cont['modifi_sum'] = 0  # 가감액 합계

            num = unpaid_orders.count() + 1 if cont['pm_cost_sum'] else unpaid_orders.count()
            rem_blank = 0 if unit_set else remaining_orders.count()
            blank_line = (15 - (num + pay_orders.count())) + rem_blank
            cont['blank_line'] = '*' * blank_line

            context['data_list'].append(cont)

        html_string = render_to_string('pdf/bill_control.html', context)

        html = HTML(string=html_string)
        html.write_pdf(target='/tmp/mypdf.pdf')

        fs = FileSystemStorage('/tmp')
        with fs.open('mypdf.pdf') as pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="payment_bill({len(contractor_id)}).pdf"'
            return response

        return response

    def overdue_rate(self, amount, days):
        if days > 0 and days < 30:
            penalty = amount * 0.08 * days / 365
        elif days < 90:
            penalty = (amount * 0.08 * 29 / 365) + (amount * 0.1 * (days - 29) / 365)
        elif days < 180:
            penalty = (amount * 0.08 * 29 / 365) + (amount * 0.1 * 59 / 365) + (amount * 0.11 * (days - 89) / 365)
        else:
            penalty = (amount * 0.08 * 29 / 365) + (amount * 0.1 * 59 / 365) + (amount * 0.11 * 89 / 365) + (amount * 0.12 * (days - 179) / 365)
        return int(penalty)


class PdfExportPayments(View):

    def get(self, request):
        context = {}
        project = request.GET.get('project')
        get_contract = request.GET.get('contract')
        context['contract'] = contract = Contract.objects.get(pk=get_contract)
        cont_date = contract.contractor.contract_date
        context['second_pay'] = second_pay = cont_date + timedelta(days=30) if contract else None
        context['ip_orders'] = ip_orders = InstallmentPaymentOrder.objects.filter(project=project)
        context['payments'] = ProjectCashBook.objects.filter(project=project, contract=contract)

        # 1. 분양가격 (차수/타입별/동호수별) 및 계약금, 중도금, 잔금 구하기
        group = contract.order_group  # 차수
        type = contract.contractunit.unit_type  # 타입
        prices = SalesPriceByGT.objects.filter(project_id=project, order_group=group, unit_type=type)  # 그룹 및 타입별 가격대
        this_price = int(round(contract.contractunit.unit_type.average_price, -4))

        try:  # 동호수
            unit = contract.contractunit.unitnumber
        except Exception:
            unit = None

        if unit:
            floor = contract.contractunit.unitnumber.floor_type
            this_price = prices.get(unit_floor_type=floor).price
        context['unit'] = unit
        context['this_price'] = this_price
        # --------------------------------------------------------------

        # 2. 실입금액
        paid_list = ProjectCashBook.objects.filter(contract=contract)
        context['now_payments'] = paid_sum = paid_list.aggregate(Sum('income'))['income__sum']  # 기 납부총액

        # 3. 납부원금 (현재 지정회차 + 납부해야할 금액 합계)
        ## 계약금 구하기
        this_orders = InstallmentPaymentOrder.objects.filter(project=project)  # 해당 건 전체 약정 회차
        down_num = this_orders.filter(pay_sort='1').count()
        try:
            dp = DownPayment.objects.get(project_id=project, order_group=contract.order_group,
                                         unit_type=contract.contractunit.unit_type)
            context['down'] = down = dp.payment_amount
        except:
            pn = round(down_num / 2)
            context['down'] = down = int(this_price * 0.1 / pn)
        down_total = down * down_num

        ## 중도금 구하기
        med_num = this_orders.filter(pay_sort='2').count()
        context['medium'] = medium = int(this_price * 0.1)
        medium_total = medium * med_num

        ## 잔금 구하기
        bal_num = this_orders.filter(pay_sort='3').count()
        context['balance'] = balance = int((this_price - down_total - medium_total) / bal_num)

        set_order1 = ip_orders.filter(pay_due_date__lt=TODAY).latest('pay_due_date')
        due_order = SalesBillIssue.objects.get(project_id=project)
        now_due_order = due_order.now_payment_order.pay_code if due_order.now_payment_order else 2
        set_order2 = ip_orders.filter(pay_time__lte=now_due_order).latest('pay_time')
        set_order = set_order1 if set_order1.pay_time >= set_order2.pay_time else set_order2
        due_installment = InstallmentPaymentOrder.objects.filter(pay_time__lte=set_order.pay_time)

        total_cont_amount = 0  # 지정회차까지 약정액 합계

        for di in due_installment:
            if di.pay_sort == '1':
                pay_amount = down
            if di.pay_sort == '2':
                pay_amount = medium
            if di.pay_sort == '3':
                pay_amount = balance
            total_cont_amount += pay_amount  # 지정회차까지 약정액 합계 (+)
        context['due_payments'] = total_cont_amount

        context['paid_orders'] = paid_orders = this_orders.filter(pay_code__lte=now_due_order)  # 지정회차까지 회차
        paid_date_list = []  # 회차별 최종 수납일자
        payments = []  # 회차별 납부금액
        adj_days = []  # 회차별 지연일수
        for po in paid_orders:
            if po.pay_time == 1 or po.pay_code == 1:
                due_date = cont_date
            elif po.pay_time == 2 or po.pay_code == 2:
                if po.pay_due_date:
                    due_date = second_pay if second_pay > po.pay_due_date else po.pay_due_date
                else:
                    due_date = second_pay
            else:
                if po.pay_due_date:
                    due_date = po.pay_due_date if po.pay_due_date > cont_date else cont_date
                else:
                    due_date = None

            pl = paid_list.filter(installment_order=po)
            pld = pl.latest('deal_date').deal_date if pl else None
            paid_date_list.append(pld)  # 회차별 최종 수납일자

            payments.append(pl.aggregate(Sum('income'))['income__sum'])  # 회차별 납부금액

            ad = pl.latest('deal_date').deal_date - due_date if pl else None
            if po.pay_time <= 2:
                add = ad.days if pl and ad.days > 0 else None
            else:
                add = ad.days if pl else None
            adj_days.append(add)  # 회차별 지연일수

        context['paid_date_list'] = list(reversed(paid_date_list))  # 회차별 최종 수납일자
        context['payments'] = list(reversed(payments))  # 회차별 납부금액
        context['adj_days'] = list(reversed(adj_days))  # 회차별 지연일수

        html_string = render_to_string('pdf/payments_by_contractor.html', context)

        html = HTML(string=html_string)
        html.write_pdf(target='/tmp/mypdf.pdf')

        fs = FileSystemStorage('/tmp')
        with fs.open('mypdf.pdf') as pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="payments_contractor.pdf"'
            return response

        return response
