from django.db import models

# Create your models here.


class Librarian(models.Model):
    admin_id = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=30, unique=True)
    password = models.CharField(max_length=30)
    tel = models.CharField(max_length=15)
    c_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "Librarian"
        ordering = ["-c_time"]
        verbose_name = "图书管理员"
        verbose_name_plural = "图书管理员"


class Book(models.Model):
    bno = models.CharField(max_length=8, primary_key=True)
    category = models.CharField(max_length=10)
    title = models.CharField(max_length=40)
    press = models.CharField(max_length=30)
    year = models.IntegerField()
    author = models.CharField(max_length=20)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.IntegerField()
    stock = models.IntegerField()

    class Meta:
        db_table = "book"
        ordering = ["bno"]


class Card(models.Model):
    cno = models.CharField(max_length=7, primary_key=True)
    name = models.CharField(max_length=10)
    department = models.CharField(max_length=40)
    TYPE_CHOICE = (
        (1, 'T'),
        (2, 'G'),
        (2, 'U'),
        (4, 'O')
    )
    type = models.CharField(max_length=2, choices=TYPE_CHOICE, default='U')

    class Meta:
        db_table = "card"


class Borrow(models.Model):
    cno = models.ForeignKey('Card', on_delete=models.CASCADE)
    bno = models.ForeignKey('Book', on_delete=models.DO_NOTHING)
    borrow_date = models.DateTimeField()
    return_date = models.DateTimeField(null=True)
    admin_id = models.ForeignKey('Librarian', on_delete=models.DO_NOTHING)

    class Meta:
        db_table = "borrow"
