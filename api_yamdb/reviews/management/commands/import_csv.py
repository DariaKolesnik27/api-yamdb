import csv

from django.conf import settings
from django.core.management.base import BaseCommand

from users.models import YamdbUser
from reviews.models import (
    Category,
    Genre,
    Title,
    Review,
    Comment,
)


class Command(BaseCommand):
    help = 'Импорт данных из CSV файлов'
    data_dir = settings.BASE_DIR / 'static' / 'data'

    def handle(self, *args, **options):
        path = self.data_dir / 'users.csv'
        with open(path, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                YamdbUser.objects.get_or_create(
                    id=row['id'],
                    username=row['username'],
                    email=row['email'],
                    role=row['role'],
                    bio=row['bio'],
                    first_name=row['first_name'],
                    last_name=row['last_name']
                )
        self.stdout.write('Users импортированы')

        path = self.data_dir / 'category.csv'
        with open(path, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                Category.objects.get_or_create(
                    id=row['id'],
                    name=row['name'],
                    slug=row['slug']
                )
        self.stdout.write('Category импортированы')

        path = self.data_dir / 'genre.csv'
        with open(path, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                Genre.objects.get_or_create(
                    id=row['id'],
                    name=row['name'],
                    slug=row['slug']
                )
        self.stdout.write('Genre импортированы')

        path = self.data_dir / 'titles.csv'
        with open(path, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                Title.objects.get_or_create(
                    id=row['id'],
                    name=row['name'],
                    year=row['year'],
                    category=Category.objects.get(id=row['category'])
                )
        self.stdout.write('Title импортированы')

        path = self.data_dir / 'genre_title.csv'
        with open(path, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                title = Title.objects.get(id=row['title_id'])
                genre = Genre.objects.get(id=row['genre_id'])
                title.genre.add(genre)
        self.stdout.write('Genre_Title импортированы')

        path = self.data_dir / 'review.csv'
        with open(path, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                Review.objects.get_or_create(
                    id=row['id'],
                    title=Title.objects.get(id=row['title_id']),
                    text=row['text'],
                    author=YamdbUser.objects.get(id=row['author']),
                    score=row['score'],
                    pub_date=row['pub_date']
                )
        self.stdout.write('Review импортированы')

        path = self.data_dir / 'comments.csv'
        with open(path, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                Comment.objects.get_or_create(
                    id=row['id'],
                    review=Review.objects.get(id=row['review_id']),
                    text=row['text'],
                    author=YamdbUser.objects.get(id=row['author']),
                    pub_date=row['pub_date']
                )
        self.stdout.write('Comments импортированы')
