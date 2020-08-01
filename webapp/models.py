from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum
from math import gcd
from functools import reduce
import string
import random


def find_gcd(list):
    return reduce(gcd, list)


class Invite(models.Model):
    code = models.CharField(max_length=30)

    def generate(self):
        self.code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        return self


class Project(models.Model):
    name = models.CharField(max_length=120, verbose_name="Имя")
    state = models.CharField(max_length=30, default="ipo",
                             choices=[('ipo', 'IPO'), ('market', 'Торгуется'), ('ended', 'Завершен')],
                             verbose_name="Статус")
    members = models.ManyToManyField(User, verbose_name="Участники")

    def to_market(self):

        ask_prices = [record.amount for record in self.iporecord_set.all()]
        total_price = sum(ask_prices)

        price = find_gcd(list(map(int, ask_prices)) + [1000])

        BillingRecord(amount=total_price + 1000 * self.members.count(), comment="IPO", project=self).save()

        for record in self.iporecord_set.all():
            StockRecord(user=record.user, project=self, number=record.amount // price).save()
            StockHistory(price=price, user=record.user, project=self).save()

        for member in self.members.all():
            StockRecord(user=member, project=self, number= 1000 // price,
                        can_sell=False).save()
            StockHistory(price=price, user=member, project=self).save()

        self.state = 'market'
        self.save()

        StockHistory(price=price, project=self).save()

        self.iporecord_set.all().delete()

    def to_end(self):

        price = self.stock_price()

        for stock in self.stockrecord_set.all():
            BillingRecord(amount=price * stock.number, comment="Закрытые проекта {}".format(self.name), user=stock.user).save()

        self.stockrecord_set.all().delete()

        self.state = 'ended'
        self.save()

    def invest(self, user: User, amount):
        if self.state == 'ipo' and get_user_balance(user) >= amount:
            IpoRecord(amount=amount, user=user, project=self).save()
            BillingRecord(amount=-1 * amount, user=user, comment="Вложение в проект {}".format(self.name)).save()
            return True
        return False

    def investors_count(self):
        return self.iporecord_set.count()

    def percent_change(self):
        if self.stockhistory_set.filter(user=None).count() > 0:
            last_price = self.stockhistory_set.filter(user=None).order_by('id').last().price
            if self.stock_price() < last_price:
                return -1 * round(100 - self.stock_price() * 100 / last_price, 2)
            else:
                return round(self.stock_price() * 100 / last_price - 100, 2)
        return 0

    def percent_change_by(self, user: User):
        if self.stockhistory_set.filter(user=user).count() > 0:
            last_price = self.stockhistory_set.filter(user=user).order_by('id').last().price
        elif self.stockhistory_set.filter(user=None).count() > 0:
            last_price = self.stockhistory_set.filter(user=None).order_by('id').last().price
        else:
            return 0

        if self.stock_price() < last_price:
            return -1 * round(100 - self.stock_price() * 100 / last_price, 2)
        else:
            return round(self.stock_price() * 100 / last_price - 100, 2)

    def stock_price(self):
        stock_count = self.stockrecord_set.aggregate(Sum('number')).get('number__sum', 0) or 0
        total_price = self.billingrecord_set.aggregate(Sum('amount')).get('amount__sum', 0) or 0
        return total_price / stock_count

    def invested_by(self, user):
        return self.iporecord_set.filter(user=user).aggregate(Sum('amount')).get('amount__sum', 0) or 0

    def all_stocks_by(self, user):
        return self.stocks_by(user) + self.frozen_stocks_by(user)

    def stocks_by(self, user):
        return int(self.stockrecord_set.filter(user=user, can_sell=True).aggregate(Sum('number')).get('number__sum', 0) or 0)

    def frozen_stocks_by(self, user):
        print(1)
        return int(
            self.stockrecord_set.filter(user=user, can_sell=False).aggregate(Sum('number')).get('number__sum', 0) or 0)

    def ipo_price(self):
        return self.iporecord_set.aggregate(Sum('amount')).get('amount__sum', 0) or 0

    def price(self):
        return self.billingrecord_set.aggregate(Sum('amount')).get('amount__sum', 0) or 0

    def pay_dividents(self):
        price = self.stock_price()
        for record in self.stockrecord_set.all():
            BillingRecord(amount=record.number * price * 0.05, comment="Выплата дивидентов от проекта {}".format(self.name), user=record.user).save()

    def change(self, percent):
        StockHistory(price=self.stock_price(), project=self).save()

        amount = percent / 100

        stock_count = self.stockrecord_set.aggregate(Sum('number')).get('number__sum', 0) or 0
        price = self.stock_price()

        BillingRecord(amount=stock_count * price * amount, comment="Корректировка акций", project=self).save()

    def buy(self, user: User, number=1):
        balance = get_user_balance(user)
        price = self.stock_price() * 1.02

        if number < 1:
            return False

        if (price * number) <= balance:

            BillingRecord(amount=price * number, comment="Покупка  {} акций от {}".format(number, user.username),
                          project=self).save()
            BillingRecord(amount=-1 * price * number, comment="Покупка {} акций проекта {}".format(number, self.name),
                          user=user).save()

            if self.stockrecord_set.filter(user=user, can_sell=True).count() > 0:
                record = self.stockrecord_set.filter(user=user, can_sell=True).first()
                record.number += number
                record.save()
            else:
                StockRecord(number=number, user=user, project=self, can_sell=True).save()

            StockHistory(price=self.stock_price(), user=user, project=self).save()

            return True
        else:
            return False

    def sell(self, user: User, number=1):
        price = self.stock_price()

        if number < 1:
            return False

        if self.stocks_by(user) > 0:

            record = self.stockrecord_set.filter(user=user, can_sell=True).first()

            if record.number >= number:
                record.number -= number

                if record.number == 0:
                    record.delete()
                else:
                    record.save()

                BillingRecord(amount=-1.02 * price * number, comment="Продажа {} акций от {}".format(number, user.username),
                              project=self).save()
                BillingRecord(amount=0.98 * price * number, comment="Продажа {} акций проекта {}".format(number, self.name), user=user).save()

                return True

        return False


class StockHistory(models.Model):
    price = models.FloatField(verbose_name="Цена", default=0)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    time = models.DateTimeField(auto_now_add=True)

class BillingRecord(models.Model):
    amount = models.FloatField(verbose_name="Сумма", default=0)
    comment = models.CharField(max_length=120, verbose_name="Комментарий", default="")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)


class IpoRecord(models.Model):
    amount = models.FloatField(verbose_name="Сумма", default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)


class StockRecord(models.Model):
    number = models.FloatField(verbose_name="Количество", default=1)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
    can_sell = models.BooleanField(default=True, verbose_name="Можно продать")


def get_user_balance(user: User):
    return user.billingrecord_set.aggregate(Sum('amount')).get('amount__sum', 0) or 0