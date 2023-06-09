from django.contrib import admin
from .models import Author, Language, Genre, Book, BookInstance
from django.db.models import TextField, CharField
from django.forms import Textarea

admin.site.register(Language)
#admin.site.register(Book)
#admin.site.register(Author)
admin.site.register(Genre)
#admin.site.register(BookInstance)

class BooksAuthorInline(admin.TabularInline):
    model = Book
    extra = 0
    formfield_overrides = {
        TextField: {'widget': Textarea(attrs={'rows': 8, 'cols': 25})},
        CharField: {'widget': Textarea(attrs={'rows': 1, 'cols': 15})},
    }

# Define the admin class
class AuthorAdmin(admin.ModelAdmin):
    list_display = (
        'last_name',
        'first_name',
        'date_of_birth',
        'date_of_death',
    )
    fields = [
        'first_name',
        'last_name',
        ('date_of_birth', 'date_of_death'),
    ]
    inlines = [BooksAuthorInline]

# Register the admin class
admin.site.register(Author, AuthorAdmin)

class BooksInstanceInline(admin.TabularInline):
    model = BookInstance
    extra = 0

# Register the Admin classes for Book using the decorator
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'display_genre')
    inlines = [BooksInstanceInline]

# Register the Admin classes for BookInstance using the decorator
@admin.register(BookInstance)
class BookInstaneAdmin(admin.ModelAdmin):
    list_filter = ('status', 'due_back')
    list_display = ('book', 'status', 'borrower', 'due_back', 'id')
    fieldsets = (
        (None, {
            'fields': ('book', 'imprint', 'id')
        }),
        ('Availability', {
            'fields': ('borrower', 'status', 'due_back')
        }),
    )
