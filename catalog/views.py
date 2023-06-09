from django.shortcuts import render
from .models import Book, Author, BookInstance, Genre
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required

def index(request):
    """View function for home page of site."""

    num_books = Book.objects.count()
    num_instances = BookInstance.objects.all().count()
    books_with_the = Book.objects.filter(title__regex=r'The.*').count()
    num_genres = Genre.objects.count()
    # Count the number of genres containing 'fiction'
    fiction_genres = Genre.objects.filter(name__icontains='fiction').count()
    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    # The 'all()' is implied by default.
    num_authors = Author.objects.count()
    # Number of visits to this view, as counter in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'books_with_the': books_with_the,
        'num_genres': num_genres,
        'fiction_genres': fiction_genres,
        'num_visits': num_visits,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

class BookListView(generic.ListView):
    model = Book
    paginate_by = 10
    ordering = ['title']

class BookDetailView(generic.DetailView):
    model = Book

class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 10
    ordering = ['last_name']

class AuthorDetailView(generic.DetailView):
    model = Author

class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return (
            BookInstance.objects.filter(borrower=self.request.user)
            .filter(status__exact='o')
            .order_by('due_back')
        )

class LoanedBooksListView(PermissionRequiredMixin, generic.ListView):
    permission_required = 'catalog.can_mark_returned'
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed.html'
    paginate_by = 10

    def get_queryset(self):
        return (
            BookInstance.objects.filter(status__exact='o').order_by('due_back')
        )

# imports for renew book function
import datetime
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from catalog.forms import RenewBookForm

@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['due_back']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed'))

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'due_back': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)

# imports for editing views
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from catalog.models import Author

class AuthorCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'catalog.add_author'
    model = Author
    initial = {'date_of_death': datetime.date.today()}
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']

class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'catalog.change_author'
    model = Author
    # for fields, '__all__' is not recommended because of security reasons:
    # the form will include any new fields that a developer may add
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']

class AuthorDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'catalog.delete_author'
    model = Author
    success_url = reverse_lazy('authors')

# editing class-based views for a book
class BookCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'catalog.add_book'
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']

class BookUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'catalog.change_book'
    model = Book
    # for fields, '__all__' is not recommended because of security reasons:
    # the form will include any new fields that a developer may add
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']

class BookDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'catalog.delete_book'
    model = Book
    success_url = reverse_lazy('books')
