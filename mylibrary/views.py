from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.shortcuts import redirect
from mylibrary import models
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator
from django.db import connection, IntegrityError, transaction
from django.contrib.auth.hashers import make_password, check_password


# Create your views here.


def signup(request):
    if request.method == "POST":
        email = request.POST.get('email', None)
        password = request.POST.get('password', None)
        if email and password:
            print(email, password)
            return redirect('/index/')
    return render(request, "signup.html")


def logout(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/login/")
    request.session.flush()
    return redirect("/login/")


def login(request):
    if request.session.get('is_login', None):
        return redirect("/index/")
    if request.method == "POST":
        account = request.POST.get('user_id', None)
        password = request.POST.get('password', None)
        error_msg = "请登录！"
        # no encryption

        if account and password:
            # noinspection PyBroadException
            try:
                user = models.Librarian.objects.get(admin_id=account)
                if user.password == password:
                    request.session['is_login'] = True
                    request.session['user_id'] = user.admin_id
                    request.session['user_name'] = user.name
                    return redirect('/index/', user)
                else:
                    error_msg = "密码错误！"
            except:
                error_msg = "用户名不存在！"
            return render(request, "login.html", {"message": error_msg})
    return render(request, "login.html")


def index(request):
    user_list = models.Librarian.objects.all()
    return render(request, "index.html", {"data": user_list})


def books(request):
    try:
        cur_page = int(request.GET.get('cur_page', '1'))
    except ValueError:
        cur_page = 1

    if request.method == "POST":
        return render(request, "sort_books.html")

    pagination = Pagination.create_pagination(
        from_name='models',
        model_name='Book',
        cur_page=cur_page,
        start_page_omit_symbol='...',
        end_page_omit_symbol='...',
        one_page_data_size=8,
        show_page_item_len=40
    )
    return render(request, "books.html", locals())


def sort_books(request):
    all_books = models.Book.objects.all()
    if request.method == "POST":
        if request.POST.get("order_bno"):
            all_books = models.Book.objects.order_by("bno")
        if request.POST.get("order_title"):
            all_books = models.Book.objects.order_by("-title")
        if request.POST.get("time_up"):
            all_books = models.Book.objects.order_by("year")
        if request.POST.get("time_down"):
            all_books = models.Book.objects.order_by("-year")
        if request.POST.get("price_up"):
            all_books = models.Book.objects.order_by("price")
        if request.POST.get("price_down"):
            all_books = models.Book.objects.order_by("-price")
    return render(request, "sort_books.html", locals())


def search(request):
    if request.method == "POST":
        b_category = request.POST.get('category')
        b_title = request.POST.get('title')
        b_press = request.POST.get('press')
        b_author = request.POST.get('author')
        b_year_from = request.POST.get('year_from')
        b_year_to = request.POST.get('year_to')
        b_price_from = request.POST.get('price_from')
        b_price_to = request.POST.get('price_to')

        if not(b_category or b_title or b_press or b_author or b_year_from or b_year_to or b_price_from or b_price_to):
            message="Please input values!"
            return render(request, "search.html", {"message": message} )

        search_books = models.Book.objects.filter(
            category__icontains=b_category, title__icontains=b_title, press__icontains=b_press,
            author__icontains=b_author
        )
        if b_year_from and b_year_to:
            search_books = search_books.filter(year__range=(b_year_from, b_year_to))
        elif b_year_from:
            search_books = search_books.filter(year__gte=b_year_from)
        elif b_year_to:
            search_books = search_books.filter(year__lte=b_year_to)

        if b_price_from and b_price_to:
            search_books = search_books.filter(price__range=(b_price_from, b_price_to))
        elif b_price_from:
            search_books = search_books.filter(price__gte=b_price_from)
        elif b_price_to:
            search_books = search_books.filter(price__lte=b_price_to)

        if search_books.count() == 0:
            message = "Oops... No result!"
        else:
            ok_message = "OK"

    return render(request, "search.html", locals())


def book_manage(request):
    if request.method == "POST":
        if request.POST.get("single_add"):
            b_bno = request.POST.get('bno')
            b_category = request.POST.get('category')
            b_title = request.POST.get('title')
            b_press = request.POST.get('press')
            b_author = request.POST.get('author')
            b_year = request.POST.get('year')
            b_price = request.POST.get('price')
            b_total = request.POST.get('total')

            try:
                new_book = models.Book.objects.create(
                    bno=b_bno, category=b_category, title=b_title,press=b_press, author=b_author,
                    year=b_year, price=b_price, total=b_total, stock=b_total
                )
                messages.success(request, "Add OK!")
            except:
                messages.error(request, "Add failed...")

        if request.POST.get("multi_add"):
            myfile = request.FILES.get("myfile", None)
            if not myfile:
                messages.error(request, "No file to upload!")
                return render(request, "book_manage.html")

            #myfile.readline()
            lines = myfile.readlines()
            for row in lines[1:]:
                line = row.decode('utf-8')
                val = line.split(',')
                for item in val:
                    item.strip()
                #print(val[0])
                if not models.Book.objects.filter(bno=val[0]).exists():
                    new_books = models.Book.objects.get_or_create(
                        bno=val[0], category=val[1], title=val[2], press=val[3], year=val[4],
                        author=val[5], price=val[6], total=val[7], stock=val[8]
                    )
            messages.success(request, "MultiAdd OK!")
    return render(request, "book_manage.html", locals())


def card(request):
    if request.method == "POST":
        if request.POST.get("btn_show"):
            cards= models.Card.objects.all()
            show_message = "Show all..."
            return render(request, "card.html", {"cards": cards, "show_message": show_message})
        c_cno = request.POST.get('cno')
        c_name = request.POST.get('name')
        c_department = request.POST.get("department")
        c_type = request.POST.get("type")
        if request.POST.get("btn_add"):
            if not(c_cno and c_name and c_department and c_type):
                messages.error(request, 'Please fill all values!')
                return render(request, "card.html")
            try:
                new_card = models.Card.objects.create(cno=c_cno, name=c_name, department=c_department, type=c_type)
                messages.success(request, 'Add done!')

            except:
                messages.error(request, 'Fail to add!')

        if request.POST.get("btn_search"):
            cards = models.Card.objects.filter(
                cno__icontains=c_cno, name__icontains=c_name,
                department__icontains=c_department, type__icontains=c_type
            )
            return render(request, "card.html", locals())

        if request.POST.get("btn_delete"):
            if c_cno:
                try:
                    del_card = models.Card.objects.get(cno=c_cno)
                    borrow_record = models.Borrow.objects.filter(cno_id=c_cno, return_date=None)
                    if not borrow_record.exists():
                        del_card.delete()
                        messages.success(request, "Delete OK!")
                    else:
                        messages.error(request, "Please return all books with the card!")
                except:
                    messages.error(request, "This card does not exist!")
            else:
                messages.error(request, 'Input cno to delete!')
            return render(request, "card.html")

    return render(request, "card.html", locals())


def borrow_book(request):
    if request.method == "POST":
        if request.POST.get("btn_borrow_record"):
            c_cno = request.POST.get('cno')
            borrowed_books = []
            try:
                i_card = models.Card.objects.get(cno=c_cno)
                borrow_record = models.Borrow.objects.filter(cno=i_card, return_date=None)
                for i in borrow_record:
                    borrowed_books.extend(models.Book.objects.filter(bno=i.bno_id))
                messages.success(request, "Search OK!")
                return render(request, "borrow_book.html", locals())
            except:
                messages.error(request, "Search failed...")
                return render(request, "borrow_book.html")

        if request.POST.get("btn_borrow"):
            c_cno = request.POST.get('cno')
            b_bno = request.POST.get('bno')
            card_record = models.Borrow.objects.filter(cno_id=c_cno)
            try:
                i_card = models.Card.objects.get(cno=c_cno)
                i_book = models.Book.objects.get(bno=b_bno)
                i_admin = models.Librarian.objects.get(admin_id=request.session.get('user_id'))
                if i_book.stock:
                    try:
                        with transaction.atomic():
                            models.Borrow.objects.create(cno=i_card, bno=i_book, borrow_date=timezone.now(),
                                                     return_date=None, admin_id=i_admin)
                            i_book.stock -= 1
                            i_book.save()
                            messages.success(request, "Borrow book OK!")
                    except IntegrityError:
                        messages.error(request, "Fail to borrow...")
                    return render(request, "borrow_book.html")

                else:
                    messages.error(request, "Book out of stock!")
            except:
                messages.error(request, "Card/Book not found...")
        return render(request, "borrow_book.html", {"card_record": card_record})

    return render(request, "borrow_book.html")


def return_book(request):
    if request.method == "POST":
        if request.POST.get("btn_return_record"):
            c_cno = request.POST.get('cno')
            borrowed_books = []
            try:
                i_card = models.Card.objects.get(cno=c_cno)
                borrow_record = models.Borrow.objects.filter(cno=i_card, return_date=None)
                for i in borrow_record:
                    borrowed_books.extend(models.Book.objects.filter(bno=i.bno_id))
                messages.success(request, "Search OK!")
                return render(request, "return_book.html", locals())
            except:
                messages.error(request, "Search failed...")
                return render(request, "return_book.html")

        if request.POST.get("btn_return"):
            c_cno = request.POST.get('cno')
            b_bno = request.POST.get('bno')
            card_record = models.Borrow.objects.filter(cno_id=c_cno)
            try:
                i_card = models.Card.objects.get(cno=c_cno)
                i_book = models.Book.objects.get(bno=b_bno)
                try:
                    with transaction.atomic():
                        i_borrow = models.Borrow.objects.get(cno_id=c_cno, bno_id=b_bno, return_date=None)
                        i_borrow.return_date = timezone.now()
                        i_borrow.save()
                        i_book.stock += 1
                        i_book.save()
                        messages.success(request, "Return book OK!")
                        return render(request, "return_book.html")
                except IntegrityError:
                    messages.error(request, "The book is not in your record!")
            except:
                messages.error(request, "Card/Book not found...")

            return render(request, "return_book.html", {"card_record": card_record})

    return render(request, "return_book.html")


class Pagination(object):
    def __init__(self):
        pass

    @classmethod
    def create_pagination(self, from_name='models', model_name='Book',
                          cur_page=1, start_page_omit_symbol='...',
                          end_page_omit_symbol='...', one_page_data_size=10,
                          show_page_item_len=9):

        start_pos = (cur_page - 1) * one_page_data_size
        end_pos = start_pos + one_page_data_size

        # 查找需要的model数据
        find_objs_str = ('models.Book.objects.all()'
                         '[{start_pos}:{end_pos}]'.format(
            model_name=model_name,
            start_pos=start_pos,
            end_pos=end_pos))
        objs = eval(find_objs_str)

        # 计算总共的页数
        find_objs_count_str = 'models.Book.objects.count()'.format(
            model_name=model_name)
        all_obj_counts = eval(find_objs_count_str)
        all_page = all_obj_counts // one_page_data_size
        remain_obj = all_obj_counts % one_page_data_size
        if remain_obj > 0:
            all_page += 1

        # 限制当前页不能小于1和并且大于总页数
        cur_page = 1 if cur_page < 1 else cur_page
        cur_page = all_page if cur_page > all_page else cur_page

        # 获得显示页数的最小页
        start_page = cur_page - show_page_item_len / 2
        if start_page > all_page - show_page_item_len:
            start_page = all_page - show_page_item_len + 1
        start_page = 1 if start_page < 1 else start_page

        # 获得显示页数的最大页
        end_page = cur_page + show_page_item_len / 2
        end_page = all_page if end_page > all_page else end_page
        if end_page < show_page_item_len and all_page > show_page_item_len:
            end_page = show_page_item_len

        # 获得上一页
        pre_page = cur_page - 1
        pre_page = 1 if pre_page < 1 else pre_page

        # 获得下一页
        next_page = cur_page + 1
        next_page = all_page if next_page > all_page else next_page

        # 处理省略符，是否显示
        if start_page <= 1:
            start_page_omit_symbol = ''

        if end_page >= all_page:
            end_page_omit_symbol = ''

        # 创建能点击的展示页码
        page_items = range(start_page, end_page + 1)

        pagination = {
            'objs': objs,
            'all_obj_counts': all_obj_counts,
            'start_pos': start_pos,
            'end_pos': end_pos,
            'all_page': all_page,
            'cur_page': cur_page,
            'pre_page': pre_page,
            'next_page': next_page,
            'page_items': page_items,
            'start_page_omit_symbol': start_page_omit_symbol,
            'end_page_omit_symbol': end_page_omit_symbol,
        }

        return pagination
