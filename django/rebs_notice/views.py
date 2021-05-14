from django.db import transaction
from django.db.models import Sum
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from datetime import datetime
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, FormView

from .models import SalesBillIssue
from .forms import SalesBillIssueForm
from rebs_project.models import Project, UnitType, UnitNumber
from rebs_contract.models import OrderGroup, Contractor
from rebs_cash.models import ProjectCashBook, SalesPriceByGT, InstallmentPaymentOrder, DownPayment


TODAY = datetime.today().strftime('%Y-%m-%d')

class BillManageView(LoginRequiredMixin, ListView, FormView):
    model = Contractor
    form_class = SalesBillIssueForm
    template_name = 'rebs_notice/contractor_bill_publish.html'

    def get_paginate_by(self, queryset):
        return self.request.GET.get('limit') if self.request.GET.get('limit') else 15

    def get_bill_issue(self):
        try:
            bill_issue = SalesBillIssue.objects.get(project=self.get_project())
        except:
            bill_issue = None
        return bill_issue

    def get_project(self):
        try:
            project = self.request.user.staffauth.assigned_project
        except:
            project = Project.objects.first()
        gp = self.request.GET.get('project')
        project = Project.objects.get(pk=gp) if gp else project
        return project

    def get_form_kwargs(self):
        kwargs = super(BillManageView, self).get_form_kwargs()
        kwargs['project'] = self.get_project()
        return kwargs

    def get_form(self, form_class=None):
        initial = {}
        bill_issue = self.get_bill_issue()
        if bill_issue:
            initial['now_payment_order'] = bill_issue.now_payment_order
            initial['now_due_date'] = bill_issue.now_payment_order.pay_due_date
            initial['host_name'] = bill_issue.host_name
            initial['host_tel'] = bill_issue.host_tel
            initial['agency'] = bill_issue.agency
            initial['agency_tel'] = bill_issue.agency_tel
            initial['bank_account1'] = bill_issue.bank_account1
            initial['bank_number1'] = bill_issue.bank_number1
            initial['bank_host1'] = bill_issue.bank_host1
            initial['bank_account2'] = bill_issue.bank_account2
            initial['bank_number2'] = bill_issue.bank_number2
            initial['bank_host2'] = bill_issue.bank_host2
            initial['zipcode'] = bill_issue.zipcode
            initial['address1'] = bill_issue.address1
            initial['address2'] = bill_issue.address2
            initial['address3'] = bill_issue.address3
            initial['title'] = bill_issue.title
            initial['content'] = bill_issue.content

        return self.form_class(self.get_project(), initial=initial)

    def get_queryset(self):
        queryset = self.model.objects.filter(contract__project=self.get_project(), status='2').order_by('contract_date')
        group = self.request.GET.get('group')
        type = self.request.GET.get('type')
        dong = self.request.GET.get('dong')
        order = self.request.GET.get('order')
        q = self.request.GET.get('q')

        if group:
            queryset = queryset.filter(contract__order_group=group)
        if type:
            queryset = queryset.filter(contract__contractunit__unit_type=type)
        if dong:
            queryset = queryset.filter(contract__contractunit__unitnumber__bldg_no=dong)
        order_list = ['contract_date', '-contract_date', 'contract__serial_number',
                      '-contract__serial_number', 'name', '-name']
        if order:
            queryset = queryset.order_by(order_list[int(order)])
        if q:
            queryset = queryset.filter(name__icontains=q)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(BillManageView, self).get_context_data(**kwargs)
        context['project_list'] = self.request.user.staffauth.allowed_projects.all()
        context['this_project'] = self.get_project()
        context['today'] = TODAY
        context['groups'] = OrderGroup.objects.filter(project=self.get_project())
        context['types'] = UnitType.objects.filter(project=self.get_project())
        context['dongs'] = UnitNumber.objects.filter(project=self.get_project()).values('bldg_no').distinct()
        context['bill_issue'] = self.get_bill_issue()

        # 계약자 별 총 납입금 계산
        paginator = Paginator(self.get_queryset(), self.get_paginate_by(self.get_queryset()))
        page = self.request.GET.get('page') if self.request.GET.get('page') else 1
        paginate_queryset = paginator.page(page)

        # 계약자별 납부상태 구하기 + 계약자별 현 회차 상태(완납회차 계산)
        now_pay_code = self.get_bill_issue().now_payment_order.pay_code if self.get_bill_issue() else 2  # 현재 납부해야 하는 회차

        total_pay_by_contract = []
        amounts = []
        paid_order = []
        for contractor in paginate_queryset:
            contract = contractor.contract
            payment_by_cont = ProjectCashBook.objects.filter(is_contract_payment=True, contract=contract).aggregate(Sum('income'))['income__sum']
            total_pay_by_contract.append(payment_by_cont) # 계약자별 총 납입액 배열화
            try: # 동호수 지정여부
                unit_set = contract.contractunit.unitnumber
            except:
                unit_set = None
            group = contract.order_group
            type = contract.contractunit.unit_type

            prices = SalesPriceByGT.objects.filter(project=self.get_project(), order_group=group, unit_type=type) # 타입별 분양가 그룹
            price = contract.contractunit.unit_type.average_price # 동호 미지정시 타입별 평균 분양가
            if unit_set:
                floor = contract.contractunit.unitnumber.floor_type
                price = prices.get(unit_floor_type=floor) # 동호 지정시 해당 동호 분양가

            # all_pay = price.installmentpaymentamount_set.all() # 분양가 -> 회차별 납입가 그룹
            # now_pay = all_pay.filter(payment_order__pay_code__lte=now_pay_code) # 회차별 납입가 중 -> 현재 회차까지 그룹
            # -----

            all_pay_order = InstallmentPaymentOrder.objects.filter(project=self.get_project())
            now_pay = 0
            now_pay_order = all_pay_order.filter(pay_code__lte=now_pay_code)

            pay_by_order = 0 # 회차별 납입액 합계
            payid_by = payment_by_cont if payment_by_cont else 0 # 해당 계약건 총 기납입액
            pbo_string = '계약금미납'
            balance_order = all_pay_order.filter(pay_sort='3')
            for apo in all_pay_order:

                if apo.pay_sort == '1': # 계약금일때
                    try:
                        dp = DownPayment.objects.get(project=self.get_project(),
                                                     order_group=contract.order_group,
                                                     unit_type=contract.contractunit.unit_type)
                        down_payment = dp.payment_amount
                    except:
                        pay_num = all_pay_order.filter(pay_sort='1').count()
                        pn = round(pay_num / 2)
                        down_payment = int(price * 0.1 / pn)
                    if apo.pay_code <= now_pay_code:
                        now_pay += down_payment
                    pay_by_order += down_payment # 회차별 납입액 가산
                    if payid_by >= pay_by_order:
                        pbo_string = apo.pay_name
                    else:
                        break

                if apo.pay_sort == '2': # 중도금일때
                    medium_amount = int(price * 0.1)
                    pay_by_order += medium_amount # 회차별 납입액 가산
                    if apo.pay_code <= now_pay_code:
                        now_pay += down_payment
                    if payid_by >= pay_by_order:
                        pbo_string = apo.pay_name
                    else:
                        break

                if apo.pay_sort == '3': # 잔금일때
                    balance_amount = int((price - pay_by_order) / balance_order.count())
                    pay_by_order += balance_amount # 회차별 납입액 가산
                    if apo.pay_code <= now_pay_code:
                        now_pay += down_payment
                    if payid_by >= pay_by_order:
                        pbo_string = apo.pay_name
                    else:
                        break

            paid_order.append(pbo_string)
            amounts.append(now_pay)
        context['total_pay_by_contract'] = list(reversed(total_pay_by_contract))
        context['amounts'] = list(reversed(amounts))
        context['paid_order'] = list(reversed(paid_order))

        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(self.get_project(), request.POST)

        if form.is_valid():
            with transaction.atomic():  # 트랜잭션

                if form.cleaned_data.get('now_due_date') != self.get_bill_issue().now_payment_order.pay_due_date:
                    now_due_order = InstallmentPaymentOrder.objects.get(pk=request.POST.get('now_payment_order'))
                    now_due_order.pay_due_date = form.cleaned_data.get('now_due_date')
                    now_due_order.save()

                if self.get_bill_issue():
                    bill_issue = SalesBillIssue.objects.get(project=self.get_project())
                    bill_issue.project = self.get_project()
                    bill_issue.now_payment_order = form.cleaned_data.get('now_payment_order')
                    bill_issue.host_name = form.cleaned_data.get('host_name')
                    bill_issue.host_tel = form.cleaned_data.get('host_tel')
                    bill_issue.agency = form.cleaned_data.get('agency')
                    bill_issue.agency_tel = form.cleaned_data.get('agency_tel')
                    bill_issue.bank_account1 = form.cleaned_data.get('bank_account1')
                    bill_issue.bank_number1 = form.cleaned_data.get('bank_number1')
                    bill_issue.bank_host1 = form.cleaned_data.get('bank_host1')
                    bill_issue.bank_account2 = form.cleaned_data.get('bank_account2')
                    bill_issue.bank_number2 = form.cleaned_data.get('bank_number2')
                    bill_issue.bank_host2 = form.cleaned_data.get('bank_host2')
                    bill_issue.zipcode = form.cleaned_data.get('zipcode')
                    bill_issue.address1 = form.cleaned_data.get('address1')
                    bill_issue.address2 = form.cleaned_data.get('address2')
                    bill_issue.address3 = form.cleaned_data.get('address3')
                    bill_issue.title = form.cleaned_data.get('title')
                    bill_issue.content = form.cleaned_data.get('content')
                    bill_issue.register = request.user
                else:
                    bill_issue = SalesBillIssue(project=self.get_project(),
                                                now_payment_order=form.cleaned_data.get('now_payment_order'),
                                                host_name=form.cleaned_data.get('host_name'),
                                                host_tel=form.cleaned_data.get('host_tel'),
                                                agency=form.cleaned_data.get('agency'),
                                                agency_tel=form.cleaned_data.get('agency_tel'),
                                                bank_account1=form.cleaned_data.get('bank_account1'),
                                                bank_number1=form.cleaned_data.get('bank_number1'),
                                                bank_host1=form.cleaned_data.get('bank_host1'),
                                                bank_account2=form.cleaned_data.get('bank_account2'),
                                                bank_number2=form.cleaned_data.get('bank_number2'),
                                                bank_host2=form.cleaned_data.get('bank_host2'),
                                                zipcode=form.cleaned_data.get('zipcode'),
                                                address1=form.cleaned_data.get('address1'),
                                                address2=form.cleaned_data.get('address2'),
                                                address3=form.cleaned_data.get('address3'),
                                                title=form.cleaned_data.get('title'),
                                                content=form.cleaned_data.get('content'),
                                                register=request.user)
                bill_issue.save()
                page = '?page=' + self.request.GET.get('page') if self.request.GET.get('page') else ''
                return redirect(reverse_lazy('rebs:notice:bill') + page)

        return render(request, 'rebs_notice/contractor_bill_publish.html', {'form': form})
