from django.shortcuts import render
from django.views.generic import View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
# --------------------------------------------------------
from datetime import timedelta
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML

from django.db.models import Sum
from rebs_project.models import Project
from rebs_contract.models import Contract
from rebs_notice.models import SalesBillIssue
from rebs_cash.models import (SalesPriceByGT, ProjectCashBook,
                              InstallmentPaymentOrder, DownPayment)


class Dashboard(LoginRequiredMixin, TemplateView):
    template_name = 'rebs/main/1_1_dashboard.html'

def memu2_1(request):
    return render(request, 'rebs/main/2_1_schedule.html')


class ExportPdfBill(View):
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
            cont['contract'] = contract = Contract.objects.get(contractor__id=id) # 해당 계약건

            # 1. 차수/타입별/동호수별 분양가 및 계약금 + 중도금 + 잔금 구하기
            group = contract.order_group # 차수
            type = contract.contractunit.unit_type # 타입
            try: # 동호수
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
            cont['medium'] = medium = int(this_price*0.1)
            medium_total = medium * med_num

            # 잔금 구하기
            bal_num = this_orders.filter(pay_sort='3').count()
            cont['balance'] = balance = int((this_price - down_total - medium_total) / bal_num)
            # --------------------------------------------------------------

            # 2. 완납금액 및 완납회차 구하기
            paid_list = ProjectCashBook.objects.filter(contract=contract).order_by('installment_order', 'deal_date')
            cont['paid_sum'] = paid_sum = paid_list.aggregate(Sum('income'))['income__sum'] # 기 납부총액
            paid_sum = paid_sum if paid_sum else 0 # 기 납부총액(None 이면 0)

            paid_order_amount = 0 # 완납회차까지 약정액 합계
            total_cont_amount = 0   # 지정회차까지 약정액 합계
            pm_cost_sum = 0 # pm 용역비 누계

            for to in this_orders:
                pay_amount = 0
                if to.pay_sort == '1':
                    pay_amount = down
                if to.pay_sort == '2':
                    pay_amount = medium
                if to.pay_sort == '3':
                    pay_amount = balance

                total_cont_amount += pay_amount    # 지정회차까지 약정액 합계 (+)
                if paid_sum >= total_cont_amount:  # 기 납부총액이 약정액보다 같거나 큰지 검사
                    paid_order = to.pay_code       # 최종 납부회차 구하기
                    paid_order_amount += pay_amount # 완납회차까지 약정액 누계
                if to.is_pm_cost:
                    pm_cost_sum += pay_amount # pm 용역비 누계
                if to.pay_code == now_due_order:   # 순회 회차가 지정회차와 같으면 순회중단
                    break

            cont['paid_orders'] = this_orders.filter(pay_code__lte=now_due_order) # 지정회차까지 회차
            due_dates = [] # 회차별 납부일자
            paid_dates = [] # 회차별 최종 수납일자
            payments = [] # 회차별 납부금액
            adj_days = [] # 회차별 지연일수
            for po in cont['paid_orders']:
                if po.pay_time == 1 or po.pay_code == 1:
                    due_date = contract.contractor.contract_date
                elif po.pay_time == 2 or po.pay_code == 2:
                    due_date = contract.contractor.contract_date + timedelta(days=30)
                else:
                    due_date = po.pay_due_date

                due_dates.append(due_date) # 회차별 납부일자
                pl = paid_list.filter(installment_order=po)
                pld = pl.latest('deal_date').deal_date if pl else None
                paid_dates.append(pld) # 회차별 최종 수납일자
                payments.append(pl.aggregate(Sum('income'))['income__sum']) # 회차별 납부금액
                ad = pl.latest('deal_date').deal_date - due_date if pl else None
                add = ad.days if pl else None
                adj_days.append(add)  # 회차별 지연일수

            cont['due_dates'] = list(reversed(due_dates)) # 회차별 납부일자
            cont['paid_dates'] = list(reversed(paid_dates)) # 회차별 최종 수납일자
            cont['payments'] = list(reversed(payments)) # 회차별 납부금액
            cont['adj_days'] = list(reversed(adj_days)) # 회차별 지연일수
            # --------------------------------------------------------------

            # 3. 미납 회차 (지정회차 - 완납회차)
            cont['second_date'] = contract.contractor.contract_date + timedelta(days=30)
            unpaid_orders_all = this_orders.filter(pay_code__gt=paid_order) # 최종 기납부회차 이후 납부회차
            cont['unpaid_orders'] = unpaid_orders = unpaid_orders_all.filter(pay_code__lte=now_due_order) # 최종 기납부회차 이후부터 납부지정회차 까지 회차그룹
            cont['unpaid_amounts_sum'] = unpaid_amounts_sum = total_cont_amount - paid_order_amount
            # --------------------------------------------------------------

            # 5. 미납 금액 (약정금액 - 납부금액)
            cont['cal_unpaid'] = cal_unpaid = paid_order_amount - paid_sum
            cont['cal_unpaid_sum'] = cal_unpaid_sum = total_cont_amount - paid_sum
            cont['arrears'] = 0 # 연체료 - 향후 연체료 계산 변수
            cont['arrears_sum'] = arrears_sum = 0 # 연체료 합계 - 향후 연체료 합계 계산 변수
            cont['pm_cost_sum'] = pm_cost_sum

            # 6. 잔여 약정 목록
            cont['remaining_orders'] = remaining_orders = this_orders.filter(pay_code__gt=now_due_order)
            if not unit_set:
                cont['remaining_orders'] = remaining_orders.filter(pay_sort='1')
            cont['modi_dates'] = 0 # 선납 or 지연 일수
            cont['modifi'] = 0     # 선납할인 or 연체 가산금계산
            cont['modifi_sum'] = 0 # 가감액 합계

            num = unpaid_orders.count() + 1 if cont['pm_cost_sum'] else unpaid_orders.count()
            rem_blank = 0 if unit_set else remaining_orders.count()
            blank_line = (14 - (num + pay_orders.count())) + rem_blank
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


class PaymentList(View):

    def get(self, request):
        context = {}
        project = request.GET.get('project')
        contract = request.GET.get('contract')
        context['contract'] = Contract.objects.get(pk=contract)
        context['second_pay'] = context['contract'].contractor.contract_date + timedelta(days=30) if context['contract'] else None
        context['ip_orders'] = InstallmentPaymentOrder.objects.filter(project=project)
        context['payments'] = ProjectCashBook.objects.filter(project=project, contract=contract)

        # 해당 세대 분양가
        try:
            unit = context['contract'].contractunit.unitnumber
        except:
            unit = None
        project = Project.objects.get(pk=project)
        unit_set = project.is_unit_set and unit
        this_price = 0
        sales_price = SalesPriceByGT.objects.filter(project=project,
                                                    order_group=context['contract'].order_group,
                                                    unit_type=context['contract'].contractunit.unit_type)
        this_price = sales_price.get(unit_floor_type=context['contract'].contractunit.unitnumber.floor_type) \
                     if unit_set else None
        context['this_price'] = this_price
        context['now_payments'] = 40000000
        context['due_payments'] = 40000000

        html_string = render_to_string('pdf/payments_by_contractor.html', context)

        html = HTML(string=html_string)
        html.write_pdf(target='/tmp/mypdf.pdf')

        fs = FileSystemStorage('/tmp')
        with fs.open('mypdf.pdf') as pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="payments_contractor.pdf"'
            return response

        return response
