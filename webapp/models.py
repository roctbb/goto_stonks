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
    state = models.CharField(max_length=30, default="ipo", choices=[('ipo', 'IPO'), ('market', 'Торгуется'), ('ended', 'Завершен')], verbose_name="Статус")
    members = models.ManyToManyField(User, verbose_name="Участники")

    def to_market(self):

        ask_prices = [record.amount for record in self.iporecord_set.all()]
        ask_count = len(ask_prices)
        total_price = sum(ask_prices)

        price = find_gcd(ask_prices + [total_price // self.members.count()])

        BillingRecord(amount=total_price * 2, comment="IPO", project=self).save()

        for record in self.iporecord_set.all():
            StockRecord(user=record.user, project=self, number=record.amount // price).save()

        for member in self.members.all():
            StockRecord(user=member, project=self, number=total_price // self.members.count() // price, can_sell=False).save()

        self.state = 'market'
        self.save()

        self.iporecord_set.all().delete()

    def to_end(self):

        price = self.stock_price()

        for stock in self.stockrecord_set.all():
            BillingRecord(amount=price*stock.number, comment="trade close", user=stock.user)

        self.stockrecord_set.all().delete()

        self.state = 'ended'
        self.save()

    def stock_price(self):
        stock_count = self.stockrecord_set.aggregate(Sum('number'))
        total_price = self.billingrecord_set.aggregate(Sum('amount'))
        return total_price // stock_count

    def price(self):
        return self.billingrecord_set.aggregate(Sum('amount'))

    def change(self, percent):
        amount = percent / 100

        stock_count = self.stockrecord_set.aggregate(Sum('number'))
        price = self.stock_price()

        BillingRecord(amount=stock_count * price * amount, comment="Manual change", project=self).save()

    def buy(self, user:User, number=1):
        balance = get_user_balance(user)
        price = self.stock_price() * 1.05

        if price * number >= balance:
            BillingRecord(amount=price * number, comment="Buy {} by {}".format(number, user.email), project=self).save()
            BillingRecord(amount=-1 * price * number, comment="Buy {} of {}".format(number, self.name), user=user).save()

            if self.stockrecord_set.filter(user=user).count() > 0:
                record = self.stockrecord_set.filter(user=user).first()
                record.number += number
                record.save()
            else:
                StockRecord(number=number, user=user, project=self, can_sell=True).save()


            return True
        else:
            return False

    def sell(self, user:User, number=1):
        price = self.stock_price() * 0.95

        if self.stockrecord_set.filter(user=user).count() > 0:

            record = self.stockrecord_set.filter(user=user).first()

            if record.number >= number:
                record.number -= number
                if record.number == 0:
                    record.delete()
                else:
                    record.save()

                BillingRecord(amount=-1 * price * number, comment="Sell {} by {}".format(number, user.email),
                              project=self).save()
                BillingRecord(amount=price * number, comment="Buy {} of {}".format(number, self.name), user=user).save()

        return False


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

def get_user_balance(user:User):
    return user.billingrecord_set.aggregate(Sum('amount'))