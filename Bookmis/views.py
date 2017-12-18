from datetime import datetime
from datetime import timedelta
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib import auth
from django.core.urlresolvers import reverse
from Bookmis.utils import permission_check
from Bookmis.models import *
# Create your views here.


#主页
def index(request):
    user=request.user if request.user.is_authenticated() else None
    content={
        'active_menu': 'homepage',
        'user': user,
    }
    return render(request,'Bookmis/index.html',content)


#办理借书证
def signup(request):
    user=request.user if request.user.is_authenticated() else None
    state = None
    if request.method=='POST':
        password=request.POST.get('password','')
        repeat_password=request.POST.get('repeat_password','')
        if password == '' or repeat_password == '':
            state = 'empty'
        elif password != repeat_password:
            state = 'repeat_error'
        else:
            username=request.POST.get('username', '')
            if User.objects.filter(username=username):
                state = 'user_exist'
            else:
                new_user=User.objects.create_user(username=username, password=password,
                                                  email=request.POST.get('email', ''))
                new_user.save()
                new_myuser=MyUser(user=new_user, birthday=request.POST.get('birthday', ''),
                                  sex=request.POST.get('sex', ''), phone=request.POST.get('phone', ''))
                new_myuser.save()
                state = 'success'
    content={
        'active_menu': 'signup',
        'state': state,
        'user': user,
    }
    return render(request,'Bookmis/signup.html',content)


#登录
def login(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('homepage'))
    state = None
    if request.method == 'POST':
        username=request.POST.get('username', '')
        password=request.POST.get('password', '')
        login_user=User.objects.get(username=username)
        if login_user.user.isloss == '是':
            state = 'loss'
            content = {
                'active_menu': 'homepage',
                'state': state,
                'user': None,
            }
            return render(request, 'Bookmis/login.html', content)
        user=auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return HttpResponseRedirect(reverse('homepage'))
        else:
            state = 'not_exist_or_password_error'
    content={
        'active_menu': 'homepage',
        'state': state,
        'user': None
    }
    return render(request, 'Bookmis/login.html', content)


#登出
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('homepage'))

@login_required
#修改密码
def set_password(request):
    user=request.user
    state=None
    if request.method=='POST':
        old_password=request.POST.get('old_password', '')
        new_password=request.POST.get('new_password', '')
        repeat_password=request.POST.get('repeat_password', '')
        if user.check_password(old_password):
            if not new_password:
                state = 'empty'
            elif new_password != repeat_password:
                state = 'repeat_error'
            else:
                user.setpassword(new_password)
                user.save()
                state='success'
        else:
            state='password_error'
    content={
        'active_menu': 'homepage',
        'user': user,
        'state': state,
    }
    return render(request,'Bookmis/set_password.html',content)


@user_passes_test(permission_check)
#添加图书
def add_book(request):
    user=request.user
    state=None
    if request.method=='POST':
        new_book=Book(
            bookID=request.POST.get('bookID', ''),
            bookname=request.POST.get('bookname', ''),
            author=request.POST.get('author', ''),
            price=request.POST.get('price', 0),
            categoryID=request.POST.get('categoryID', 0),
            publishing=request.POST.get('publishing', ''),
            quantityIN=request.POST.get('quantityIN', 0)
        )
        new_book.save()
        state='success'
    content={
        'active_menu': 'add_book',
        'user': user,
        'state': state,
    }
    return render(request,'Bookmis/add_book.html', content)


#检索与查看图书
def view_book(request):
    user=request.user if request.user.is_authenticated() else None
    category_list = BookCategory.objects.values_list('categoryName', flat=True)
    query_category = request.GET.get('category', 'all')
    if (not query_category) or BookCategory.objects.filter(categoryName=query_category).count() is 0:
        query_category = 'all'
        book_list = Book.objects.all()
    else:
        bookcategory=BookCategory.objects.get(categoryName=query_category)
        book_list=Book.objects.filter(categoryID=bookcategory.categoryID)
    if request.method == 'POST':
        bkname = request.POST.get('bkname', '')
        bkauthor=request.POST.get('bkauthor', '')
        if bkname !='':
            book_list = Book.objects.filter(bookname__contains=bkname)
            query_category = 'all'
        if bkauthor !='':
            book_list=Book.objects.filter(author__contains=bkauthor)
            query_category='all'
    paginator = Paginator(book_list, 5)
    page = request.GET.get('page')
    try:
        book_list = paginator.page(page)
    except PageNotAnInteger:
        book_list = paginator.page(1)
    except EmptyPage:
        book_list = paginator.page(paginator.num_pages)
    content = {
        'user': user,
        'active_menu': 'view_book',
        'category_list': category_list,
        'query_category': query_category,
        'book_list': book_list,
    }
    return render(request, 'Bookmis/view_book_list.html', content)


def detail(request):
    user=request.user if request.user.is_authenticated() else None
    book_id=request.GET.get('id', '')
    if book_id == '':
        return HttpResponseRedirect(reverse('view_book'))
    try:
        book = Book.objects.get(bookID=book_id)
    except book.DoesNotExist:
        return HttpResponseRedirect(reverse('view_book'))

    content = {
        'user': user,
        'book': book,
        'active_menu': 'view_book',
    }
    return render(request,'Bookmis/detail.html',content)


#借阅图书
def borrow(request):
    if request.method == 'POST':
        book_id=request.POST.get('book_id', '')
        username=request.POST.get('username', '')
        try:
            my_user=User.objects.get(username__exact=username)
            if my_user.user.isloss=='是':
                state='loss'
                content={
                    'state': state,
                    'active_menu': 'borrow',
                    'my_user':my_user,
                }
                return render(request, 'Bookmis/borrow.html', content)
        except :
            state='no_user'
            content={
                'state': state,
                'active_menu': 'borrow',
                'my_user': None,
            }
            return render(request,'Bookmis/borrow.html',content)
        if book_id == '':
            return HttpResponseRedirect(reverse('homepage'))
        else:
            book = Book.objects.get(bookID=book_id)
            if my_user.user.book_num == my_user.user.level.maxbooknum:
                state = 'max_book'
                content = {
                    'state': state,
                    'active_menu': 'borrow',
                    'my_user': my_user,
                }
                return render(request,'Bookmis/borrow.html',content)

            elif book.quantityOUT  == book.quantityIN:
                state = 'max_lend'
                content = {
                    'state': state,
                    'active_menu': 'borrow',
                    'my_user': my_user,
                }
                return render(request, 'Bookmis/borrow.html', content)
            else:
                date_now=datetime.now()
                if my_user.user.level.level == '普通会员':
                    return_time=date_now+timedelta(days=30)
                elif my_user.user.level.level == '黄金会员':
                    return_time = date_now + timedelta(days=60)
                elif my_user.user.level.level == '钻石会员':
                    return_time = date_now + timedelta(days=90)
                new_borrow=Borrow(
                    reader=my_user.user,
                    book=book,
                    dateReturn=return_time.date(),
                )
                new_borrow.save()
                book.quantityOUT += 1
                book.save()
                my_user.user.book_num += 1
                my_user.user.save()
                state='success'
                content={
                    'state':state,
                    'active_menu': 'borrow',
                    'my_user': my_user,
                    'new_borrow': new_borrow,
                    'book': book,
                    }

                return render(request,'Bookmis/borrow.html', content)
    content = {
            'active_menu': 'borrow',
            }
    return render(request,'Bookmis/borrow.html',content)

#借阅信息
@login_required()
def borrow_info(request):
    user=request.user if request.user.is_authenticated() else None
    my_borrow_info = Borrow.objects.filter(reader=user.user)
    paginator = Paginator(my_borrow_info, 5)
    page = request.GET.get('page')
    try:
        my_borrow_info = paginator.page(page)
    except PageNotAnInteger:
        my_borrow_info = paginator.page(1)
    except EmptyPage:
        my_borrow_info = paginator.page(paginator.num_pages)
    content={
        'active_menu': 'borrow_info',
        'user': user,
        'my_borrow_info': my_borrow_info
    }
    return render(request,'Bookmis/borrow_info.html', content)

#还书
def return_book(request):
    user=request.user if request.user.is_authenticated() else None
    book_id=request.GET.get('id','')
    if book_id == '':
        return HttpResponseRedirect(reverse('borrow_info'))
    else:
        returned_book=Book.objects.get(bookID=book_id)
        my_borrow=Borrow.objects.get(book=returned_book)
        if my_borrow.isReturn == '是':
            state='returned'
            content = {
                'user': user,
                'active_menu': borrow_info,
                'state': state,
                'my_borrow': my_borrow
            }
            return render(request, 'Bookmis/return_book.html', content)
        else:
            my_borrow.isReturn='是'
            date_now = datetime.now()
            my_borrow.dateReturn= date_now.date()
            my_borrow.save()
            returned_book.quantityOUT -= 1
            returned_book.save()
            user.user.book_num -= 1
            user.user.save()
            state='success'
        content={
            'user': user,
            'active_menu': borrow_info,
            'state': state,
            'my_borrow': my_borrow
        }
        return render(request, 'Bookmis/return_book.html', content)

#书籍丢失
def book_lost(request):
    user=request.user if request.user.is_authenticated() else None
    book_id=request.GET.get('id','')
    lost_book=Book.objects.get(bookID=book_id)
    my_borrow=Borrow.objects.get(reader=user.user,book=lost_book)
    my_borrow.isloss = '是'
    my_borrow.save()
    lost_book.quantityLOSS += 1
    lost_book.save()
    user.user.book_num -= 1
    user.user.save()
    content={
        'user': user,
        'active_menu': 'borrow_info',
        'lost_book': lost_book,
    }
    return render(request, 'Bookmis/book_lost.html', content)


#升级会员
def level_up(request):
    user=request.user if request.user.is_authenticated() else None
    level_list=MemberLevel.objects.filter(~Q(level='管理员')).order_by('fee')
    print(level_list)
    content = {
        'user': user,
        'active_menu': 'level_up',
        'level_list': level_list
    }
    return render(request, 'Bookmis/level_up.html', content)

#开通成功页
def level_success(request):
    user = request.user if request.user.is_authenticated() else None
    new_level = request.GET.get('new_level', '')
    if new_level == '黄金会员':
        gold = MemberLevel.objects.get(level='黄金会员')
        user.user.level = gold
        user.user.save()
    if new_level == '钻石会员':
        diamond = MemberLevel.objects.get(level='钻石会员')
        user.user.level = diamond
        user.user.save()
    content = {
        'user': user,
        'active_menu': level_up,
    }
    return render(request, 'Bookmis/level_success.html', content)


#读者证挂失
def loss_report(request):
    state=None
    if request.method == 'POST':
        username=request.POST.get('username', '')
        lost_user=User.objects.get(username=username)
        my_lost_user=MyUser.objects.get(user=lost_user)
        if my_lost_user.DoesNotExist :
            state = 'empty'
        else:
            loss=LossReport(reader=my_lost_user)
            loss.save()
            my_lost_user.isloss = '是'
            my_lost_user.save()
            state='success'
    content={
        'active_menu': 'loss_report',
        'state': state,
    }
    return render(request, 'Bookmis/loss_report.html', content)


#超期未还
def late_return(request):
    now_date=datetime.now().date()
    borrow_list=Borrow.objects.filter(dateReturn__lte=now_date, isReturn='否')

    content={
        'active_menu': 'late_return',
        'borrow_list': borrow_list,
    }
    return render(request,'Bookmis/late_return.html',content)