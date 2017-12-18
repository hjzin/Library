from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class MyUser(models.Model):
    user=models.OneToOneField(User,related_name='user')
    readerID=models.AutoField(primary_key=True)
    birthday=models.DateField()
    permission=models.IntegerField(default=1)
    sex=models.CharField(max_length=3)
    phone=models.CharField(max_length=12)
    level=models.ForeignKey('MemberLevel',default='普通会员',related_name='ulevel')
    book_num=models.IntegerField(default=0)
    isloss=models.CharField(max_length=3, default='否')

    def __str__(self):
        return self.user.username

class Book(models.Model):
    bookID=models.CharField(max_length=10,primary_key=True,unique=True)
    bookname=models.CharField(max_length=128)
    author=models.CharField(max_length=128)
    price=models.FloatField()
    categoryID=models.IntegerField()
    publishing=models.CharField(max_length=128)
    dateIN=models.DateField(auto_now_add=True)
    quantityIN=models.IntegerField()
    quantityOUT=models.IntegerField(default=0)
    quantityLOSS=models.IntegerField(default=0)

    class META:
        ordering=['bookID']

    def __str__(self):
        return self.bookname


class BookCategory(models.Model):
    categoryID=models.IntegerField(primary_key=True)
    categoryName=models.CharField(max_length=128)

    class META:
        ordering=['categoryID']

    def __str__(self):
        return self.categoryID


class Borrow(models.Model):
    dateBorrow=models.DateField(auto_now_add=True)
    dateReturn=models.DateField()
    isloss=models.CharField(default='否',max_length=3)
    reader=models.ForeignKey(MyUser,related_name='userid')
    book=models.ForeignKey(Book,related_name='bookid')
    isReturn=models.CharField(max_length=3,default='否')

    class META:
        ordering=['readerID']
        unique_together=("readerID","bookID")

    def __str__(self):
        return self.reader.user.username


class MemberLevel(models.Model):
    level=models.CharField(max_length=10,primary_key=True)
    days=models.IntegerField(default=30)
    maxbooknum=models.IntegerField(default=3)
    fee=models.FloatField(default=10.0)

    def __str__(self):
        return self.level


class LossReport(models.Model):
    lossDate=models.DateField(auto_now_add=True)
    reader=models.ForeignKey(MyUser)

    class META:
        ordering=['readerID']

    def __str__(self):
        return self.reader.user.username