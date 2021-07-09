import math
from django.shortcuts import render
from django.views.generic import View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
# --------------------------------------------------------
from datetime import date, datetime, timedelta
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML

from django.db.models import Sum
from rebs_contract.models import Contract
from rebs_notice.models import SalesBillIssue
from rebs_cash.models import (SalesPriceByGT, ProjectCashBook,
                              InstallmentPaymentOrder, DownPayment)

TODAY = date.today()


class Dashboard(LoginRequiredMixin, TemplateView):
    template_name = 'rebs/main/1_1_dashboard.html'


def memu2_1(request):
    return render(request, 'rebs/main/2_1_schedule.html')


class PdfExportBill(View):
    """고지서 리스트"""

    def get(self, request):
        context = {}
        context['data_list'] = []
        project = request.GET.get('project')
        context['issue_date'] = request.GET.get('date')
        contractor_list = request.GET.get('seq').split('-')
        context['bill'] = SalesBillIssue.objects.get(project_id=project)
        installment_payment_order = InstallmentPaymentOrder.objects.filter(project_id=project)
        now_due_order = context['bill'].now_payment_order.pay_code if context['bill'].now_payment_order else 2


        # 해당 계약건에 대한 데이터 정리 --------------------------------------- start
        for cont_id in contractor_list: # 선택된 계약 건 수만큼 반복

            cont = {} # 현재 계약 정보 딕셔너리
            cont['contract'] = contract = Contract.objects.get(contractor__id=cont_id)  # 해당 계약건

            try:  # 동호수
                cont['unit'] = contract.contractunit.unitnumber
            except Exception:
                cont['unit'] = None

            # 총 공급가액(분양가) 구하기
            group = contract.order_group  # 차수
            type = contract.contractunit.unit_type  # 타입
            # 해당 계약건 분양가 # this_price = '동호 지정 후 고지'
            this_price = contract.contractunit.unit_type.average_price
            prices = SalesPriceByGT.objects.filter(project_id=project, order_group=group, unit_type=type)

            if cont['unit']:
                floor = contract.contractunit.unitnumber.floor_type
                this_price = prices.get(unit_floor_type=floor).price
            # ---------------------------------------------------------------------------

            # 계약금 구하기
            down_num = installment_payment_order.filter(pay_sort='1').count()
            try:
                dp = DownPayment.objects.get(
                    project_id=project,
                    order_group=contract.order_group,
                    unit_type=contract.contractunit.unit_type
                )
                down = dp.payment_amount
            except:
                pn = round(down_num / 2)
                down = int(this_price * 0.1 / pn)
            down_total = down * down_num
            # ---------------------------------------------------------------------------

            # 중도금 구하기
            med_num = installment_payment_order.filter(pay_sort='2').count()
            medium = int(this_price * 0.1)
            medium_total = medium * med_num
            # ---------------------------------------------------------------------------

            # 잔금 구하기
            bal_num = installment_payment_order.filter(pay_sort='3').count()
            balance = int((this_price - down_total - medium_total) / bal_num)
            # ---------------------------------------------------------------------------

            # 완납금액 구하기
            paid_list = ProjectCashBook.objects.filter(
                is_contract_payment=True,
                contract=contract,
                income__isnull=False
            ).order_by('installment_order', 'deal_date') # 해당 계약 건 납부 데이터
            paid_sum_total = paid_list.aggregate(Sum('income'))['income__sum']  # 완납 총금액
            # ---------------------------------------------------------------------------

            pay_amount_total = 0  # 납부 지정회차까지 약정금액 합계
            pay_amount_paid = 0  # 완납 회차까지 약정액 합계
            paid_pay_code = 0  # 완납회차
            pm_cost_sum = 0  # pm 용역비 누계

            late_fee_list = [] # 연체료 리스트
            payment_list = []  # 회차별 납부금액
            paid_date_list = []  # 회차별 최종 수납일자

            first_paid_date = None  # 최초 계약금 완납일

            # ---------------------------------------------------------------------- 미정리 코드
            # due_date_list = []  # 회차별 납부기한
            # def_pay_list = []  # 회차별 지연금액 리스트
            # delay_day_list = []  # 회차별 지연일수
            # late_fee_sum = 0  # 연체료 총액


            for to in installment_payment_order:
                pay_amount = 0                       # 약정금액
                if to.pay_sort == '1':
                    pay_amount = down
                if to.pay_sort == '2':
                    pay_amount = medium
                if to.pay_sort == '3':
                    pay_amount = balance

                pay_amount_total += pay_amount          # 약정금액 누계

                if paid_sum_total >= pay_amount_total:  # 기 납부총액이 약정액보다 같거나 큰지 검사
                    paid_pay_code = to.pay_code         # 완납회차 추출
                    pay_amount_paid += pay_amount       # 완납회차까지 약정액 누계

                if to.is_pm_cost:
                    pm_cost_sum += pay_amount  # pm 용역비 누계

                # 회차별 납부 해야할 금액 ----------------------------------------------------------
                now_payment = paid_list.filter(installment_order=to) # 현재 회차 납부 데이터
                paid_date = now_payment.latest('deal_date').deal_date if now_payment else None # 현재회차 최종 납부일
                now_paied_sum = now_payment.aggregate(Sum('income'))['income__sum'] # 현재 회차 납부액 합계
                paid_amount = now_paied_sum if now_paied_sum else 0

                # if to.pay_code == 1:
                    # first_paid_date = paid_date # 계약금 납부일
                payment_list.append(paid_amount)  # 회차별 납부금액
                paid_date_list.append(paid_date)  # 회차별 최종 수납일자

                # 계약일과 최초 계약금 납부일 중 늦은 날을 기점으로 30일
                # reference_date = first_paid_date if first_paid_date and (first_paid_date > contract.contractor.contract_date) else contract.contractor.contract_date
                # extra_date = reference_date if reference_date > datetime.strptime("2019-07-30", "%Y-%m-%d").date() else datetime.strptime("2019-07-30", "%Y-%m-%d").date()

                # if to.pay_time == 1 or to.pay_code == 1:  # 최초 계약금일 때
                #     due_date = contract.contractor.contract_date  # 납부기한
                #
                # elif to.pay_time == 2 or to.pay_code == 2:  # 2차 계약금일 때
                #     due_date = reference_date + timedelta(days=30)  # 납부기한 = 기준일 30일 후
                #     extra_date = datetime.strptime("2019-07-30", "%Y-%m-%d").date()
                #     if to.pay_due_date:  # 당회차 납부기한이 설정되어 있을 때 -> 계약후 30일 후와 설정일 중 늦은 날을 납부기한으로 한다.
                #         due_date = due_date if due_date > to.pay_due_date else to.pay_due_date  # 납부기한
                #
                # else:  # 3회차 이후 납부회차인 경우
                #     if to.pay_due_date:
                #         due_date = to.pay_due_date if to.pay_due_date > reference_date + timedelta(days=30) else reference_date + timedelta(days=30)  # 납부기한
                #     else:
                #         due_date = None
                #     extra_date = due_date
                #
                # due_date_list.append(due_date)  # 회차별 납부일자

                # 지연일수 및 가산금 구하기
                unpaid = pay_amount - paid_amount  # 지연금 = 약정 금액 - 납부한 금액
                late_fee_list.append(unpaid)  # 지연금 리스트
                #
                # delay_paid = paid_list.filter(installment_order__gt=to)
                # delay_paid_sum = 0  # 지연금 총 납부액
                # delay_paid_date = date.today() # 지연 기준일
                #
                # if unpaid > 0:
                #     for dp in delay_paid:
                #         delay_paid_sum += dp.income
                #         if delay_paid_sum > unpaid:
                #             delay_paid_date = dp.deal_date  # 지연금 완납일자
                #             break
                #
                # extra_paid_date = paid_date if paid_date > extra_date else extra_date
                #
                # if extra_date > delay_paid_date:
                #     delay_dates = 0   # 지연일수
                # else:
                #     delay = delay_paid_date - extra_paid_date  # 미수 완납일 - 미수 발생일
                #     delay_dates = delay.days  # 지연일수
                #
                # late_fee_sum += self.get_late_fee(unpaid, delay_dates)
                #
                # delay_day_list.append(delay_dates)  # 회차별 지연일수
                #
                if to.pay_code == now_due_order:  # 순회 회차가 지정회차와 같으면 순회중단
                    break


            # ■ 계약 내용------------------------------------------------------
            cont['price'] = this_price  # 이 건 분양가격
            # --------------------------------------------------------------

            # ■ 당회 납부대금 안내----------------------------------------------
            unpaid_orders_all = installment_payment_order.filter(pay_code__gt=paid_pay_code)  # 최종 기납부회차 이후 납부회차
            cont['unpaid_orders'] = unpaid_orders_all.filter(pay_code__lte=now_due_order)  # 최종 기납부회차 이후부터 납부지정회차 까지 회차그룹
            cont['pay_amount'] = 0
            cont['pay_amount_sum'] = 0
            for uo in cont['unpaid_orders']:
                if uo.pay_sort == '1':
                    cont['pay_amount'] = down
                elif uo.pay_sort == '2':
                    cont['pay_amount'] = medium
                else:
                    cont['pay_amount'] = balance
                cont['pay_amount_sum'] += cont['pay_amount']
            cont['cal_unpaid'] = pay_amount_paid - paid_sum_total
            cont['cal_unpaid_sum'] = pay_amount_total - paid_sum_total # 미납액 = 약정액 - 납부액

            cont['late_fee_list'] = list(reversed(late_fee_list))
            cont['late_fee_sum'] = sum(late_fee_list)  # 가산금 합계
            # --------------------------------------------------------------

            # ■ 계좌번호 안내--------------------------------------------------

            # --------------------------------------------------------------

            # ■ 납부약정 및 납입내역--------------------------------------------

            # --------------------------------------------------------------
            # cont['paid_orders'] = installment_payment_order.filter(pay_code__lte=now_due_order)  # 지정회차까지 회차
            # cont['due_date_list'] = list(reversed(due_date_list))  # 회차별 납부일자
            # cont['paid_date_list'] = list(reversed(paid_date_list))  # 회차별 최종 수납일자
            # cont['payment_list'] = list(reversed(payment_list))  # 회차별 납부금액
            # cont['delay_day_list'] = list(reversed(delay_day_list))  # 회차별 지연일수
            # cont['def_pay_list'] = list(reversed(def_pay_list))  # 회차별 지연금 리스트
            # cont['paid_sum_total'] = paid_sum_total if paid_sum_total else 0
            # --------------------------------------------------------------

            # 4. 미납 회차 (지정회차 - 완납회차)
            cont['second_date'] = contract.contractor.contract_date + timedelta(days=30)
            # --------------------------------------------------------------

            # 5. 미납 금액 (약정금액 - 납부금액)
            # cont['pay_amount_total'] = pay_amount_total
            # cont['pm_cost_sum'] = pm_cost_sum

            # 6. 잔여 약정 목록
            # cont['remaining_orders'] = remaining_orders = installment_payment_order.filter(pay_code__gt=now_due_order)
            # if not cont['unit']:
            #     cont['remaining_orders'] = remaining_orders.filter(pay_sort='1')
            # cont['modi_dates'] = 0  # 선납 or 지연 일수
            # cont['modifi'] = 0  # 선납할인 or 연체 가산금계산
            # cont['modifi_sum'] = 0  # 가감액 합계

            # num = unpaid_orders.count() + 1 if cont['pm_cost_sum'] else unpaid_orders.count()
            # rem_blank = 0 if cont['unit'] else remaining_orders.count()
            # blank_line = (15 - (num + installment_payment_order.count())) + rem_blank
            # cont['blank_line'] = '*' * blank_line

            context['data_list'].append(cont)
        # 해당 계약건에 대한 데이터 정리 --------------------------------------- end

        html_string = render_to_string('pdf/bill_control.html', context)

        html = HTML(string=html_string)
        html.write_pdf(target='/tmp/mypdf.pdf')

        fs = FileSystemStorage('/tmp')
        with fs.open('mypdf.pdf') as pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="payment_bill({len(contractor_list)}).pdf"'
            return response

    def get_late_fee(self, amount, days):
        if amount < 0:
            late_fee = (amount * 0.04 * days / 365) * -1
        else:
            if days < 30:
                late_fee = amount * 0.08 * days / 365
            elif days < 90:
                late_fee = (amount * 0.08 * 29 / 365) + (amount * 0.1 * (days - 29) / 365)
            elif days < 180:
                late_fee = (amount * 0.08 * 29 / 365) + (amount * 0.1 * 60 / 365) + (amount * 0.11 * (days - 89) / 365)
            else:
                late_fee = (amount * 0.08 * 29 / 365) + (amount * 0.1 * 60 / 365) + (amount * 0.11 * 90 / 365) + (amount * 0.12 * (days - 179) / 365)
        return math.floor(late_fee / 1000) * 1000


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
        context['now_payments'] = paid_sum_total = paid_list.aggregate(Sum('income'))['income__sum']  # 기 납부총액

        # 3. 납부원금 (현재 지정회차 + 납부해야할 금액 합계)
        ## 계약금 구하기
        installment_payment_order = InstallmentPaymentOrder.objects.filter(project=project)  # 해당 건 전체 약정 회차
        down_num = installment_payment_order.filter(pay_sort='1').count()
        try:
            dp = DownPayment.objects.get(project_id=project, order_group=contract.order_group,
                                         unit_type=contract.contractunit.unit_type)
            context['down'] = dp.payment_amount
        except:
            pn = round(down_num / 2)
            context['down'] = int(this_price * 0.1 / pn)
        down_total = context['down'] * down_num

        ## 중도금 구하기
        med_num = installment_payment_order.filter(pay_sort='2').count()
        context['medium'] = int(this_price * 0.1)
        medium_total = context['medium'] * med_num

        ## 잔금 구하기
        bal_num = installment_payment_order.filter(pay_sort='3').count()
        context['balance'] = int((this_price - down_total - medium_total) / bal_num)

        set_order1 = ip_orders.filter(pay_due_date__lt=TODAY).latest('pay_due_date')
        due_order = SalesBillIssue.objects.get(project_id=project)
        now_due_order = due_order.now_payment_order.pay_code if due_order.now_payment_order else 2
        set_order2 = ip_orders.filter(pay_time__lte=now_due_order).latest('pay_time')
        set_order = set_order1 if set_order1.pay_time >= set_order2.pay_time else set_order2
        due_installment = InstallmentPaymentOrder.objects.filter(pay_time__lte=set_order.pay_time)

        pay_amount_total = 0  # 지정회차까지 약정액 합계

        for di in due_installment:
            if di.pay_sort == '1':
                pay_amount = context['down']
            if di.pay_sort == '2':
                pay_amount = context['medium']
            if di.pay_sort == '3':
                pay_amount = context['balance']
            pay_amount_total += pay_amount  # 지정회차까지 약정액 합계 (+)
        context['due_payments'] = pay_amount_total

        context['paid_orders'] = paid_orders = installment_payment_order.filter(pay_code__lte=now_due_order)  # 지정회차까지 회차
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
