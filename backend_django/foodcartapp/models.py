from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Sum
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderQuerySet(models.QuerySet):

    def get_order_price(self):
        amount = self.prefetch_related('items').prefetch_related('items__product').select_related(
            'restaurant').order_by('-status').annotate(
            order_price=Sum(F('items__quantity') * F('items__price'))
        )
        return amount


class Order(models.Model):
    STATUS_CHOICES = [
        ('unprocessed', 'Необработанный'),
        ('prepair to ship', 'Сборка заказа'),
        ('delivery', 'Доставка заказа'),
        ('delivered', 'Товар доставлен'),
    ]
    PAYMENT_CHOICES = [
        ('cash', 'Наличностью'),
        ('card', 'Электронно'),
        ('missed', 'Не указано'),
    ]
    firstname = models.CharField(verbose_name='Имя клиента', max_length=50)
    lastname = models.CharField(verbose_name='Фамилия клиента', max_length=50)
    phonenumber = PhoneNumberField(verbose_name='Номер телефона')
    address = models.CharField(verbose_name='Адрес', max_length=200)
    status = models.CharField(
        verbose_name='Статус заказа',
        max_length=50,
        choices=STATUS_CHOICES,
        default='unprocessed',
        db_index=True)
    comment = models.TextField(verbose_name='Коментарий к заказу', blank=True)
    created = models.DateTimeField(
        verbose_name='Дата и время создания заказа',
        default=timezone.now, db_index=True)
    called = models.DateTimeField(
        verbose_name='Дата и время прозвона заказа',
        db_index=True,
        blank=True,
        null=True)
    delivered = models.DateTimeField(
        verbose_name='Дата и время доставки заказа',
        db_index=True,
        blank=True,
        null=True)
    payment_method = models.CharField(
        verbose_name='Способ оплаты',
        max_length=50,
        choices=PAYMENT_CHOICES,
        db_index=True,
        default='missed'
    )
    restaurant = models.ForeignKey(Restaurant, verbose_name='Ресторан', related_name='orders',
                                   on_delete=models.CASCADE, null=True, blank=True)
    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f'{self.firstname} {self.lastname}, {self.address}'


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE,  verbose_name='Товар', related_name='items')
    order = models.ForeignKey(Order, on_delete=models.CASCADE,  verbose_name='Заказ', related_name='items')
    quantity = models.IntegerField(verbose_name='Количество', validators=[MinValueValidator(1)])
    price = models.DecimalField('цена', max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])

    class Meta:
        verbose_name = 'Элемент заказа'
        verbose_name_plural = 'Элементы заказа'

    def __str__(self):
        return f'{self.product}, {self.order}'
