from django.shortcuts import render, redirect , get_object_or_404 
from django.views import View
from django.middleware.csrf import get_token

class HomeView(View):
    def get(self, request):
        return render(request, 'user/index.html')
    

import pandas as pd
from django.shortcuts import render
from django.http import HttpResponse

from .forms import ExcelUploadForm
from core_app.models import BookName , Books_Category
def upload_excel(request):
    csrf_token = get_token(request)
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['excel_file']
            df = pd.read_excel(excel_file)

            # Iterate over the rows in the DataFrame and create model instances
            for index, row in df.iterrows():
                book_category = Books_Category.objects.get(book_category = row['Book Category ID'])
                BookName.objects.create(
                    book_category_id = book_category ,
                    book_name = row['Book Name'] ,
                    book_author_name = row['Book Author Name']
                )
                print(row['Book Name'] ,'---',row['Book Author Name'],'---',row['Book Category ID'] )

            return HttpResponse('Data imported successfully')

    else:
        form = ExcelUploadForm()

    return render(request, 'upload.html', {'csrf_token': csrf_token})
