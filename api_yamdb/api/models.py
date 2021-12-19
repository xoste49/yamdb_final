from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .validators import year_validator


class Confirmation(models.Model):
    key = models.CharField(max_length=50)
    email = models.EmailField()


class User(AbstractUser):
    USER = 'user'
    MODER = 'moderator'
    ADMIN = 'admin'
    ROLES = [
        (USER, 'Пользователь'),
        (MODER, 'Модератор'),
        (ADMIN, 'Администратор'),
    ]
    role = models.TextField(
        blank=True,
        choices=ROLES,
    )
    bio = models.CharField(
        blank=True,
        max_length=100
    )
    description = models.CharField(
        blank=True,
        max_length=100
    )
    email = models.EmailField(unique=True)

    @property
    def is_admin(self):
        return bool(
            self.role == self.ADMIN
            or self.is_superuser
        )

    @property
    def is_moderator(self):
        return self.role == self.MODER

    def __str__(self):
        return self.username


class Category(models.Model):
    name = models.CharField(
        verbose_name='Название категории',
        max_length=20,
    )
    slug = models.SlugField(
        verbose_name='Slug категории',
        unique=True
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(models.Model):
    name = models.CharField(
        verbose_name='Название жанра',
        max_length=20,
    )
    slug = models.SlugField(
        verbose_name='Slug жанра',
        unique=True
    )

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    name = models.CharField(
        verbose_name='Название произведения',
        max_length=100,
    )
    year = models.IntegerField(
        verbose_name='Год создания',
        validators=[year_validator],
    )
    category = models.ForeignKey(
        Category,
        null=True,
        on_delete=models.SET_NULL,
        related_name='titles',
        verbose_name='Категория'
    )
    genre = models.ManyToManyField(
        Genre,
        db_table='api_genre_title',
        verbose_name='Жанры произведения',
        related_name='titles'
    )
    description = models.TextField(
        verbose_name='Описание произведения',
        blank=True,
        null=False,
        default=''
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'


class Review(models.Model):
    """
    Ресурс REVIEWS: отзывы на произведения.
    Отзыв привязан к определённому произведению.

    Parameters
    ----------
    title : Title
        Объект для оценки
    text : string
        Текст отзыва
    author : User
        Пользователя
    score : Int
        Оценка от 1 до 10
    pub_date : DateTime
        Дата публикации отзыва
    """
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        db_column='title_id',
        related_name='reviews',
        verbose_name='Произведение',
    )
    text = models.CharField(
        'Текст отзыва',
        max_length=1500,
        help_text='Максимальная длина 1500 символов'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        db_column='author',
        verbose_name='Автор',
    )
    score = models.IntegerField(
        'Оценка',
        validators=[
            MinValueValidator(1, message='Оценка не может быть меньше 1'),
            MaxValueValidator(10, message='Оценка не может быть больше 10')
        ],
        default=1
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ('pub_date',)

    def __str__(self):
        return self.text[:40] + '...'


class Comment(models.Model):
    """
    Ресурс COMMENTS: комментарии к отзывам.
    Комментарий привязан к определённому отзыву.

    Parameters
    ----------
    review : Review
        Объект отзыва
    text : string
        Текст комментария
    author : User
        Автор комментария
    pub_date : DateTime
        Дата публикации комментария
    """
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв',
    )
    text = models.CharField(
        'Текст комментария',
        max_length=1500,
        help_text='Максимальная длина 1500 символов'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        db_column='author',
        verbose_name='Автор',
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('pub_date',)

    def __str__(self):
        return self.text[:40] + '...'
