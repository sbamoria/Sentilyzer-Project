from django.http.response import HttpResponse
from django.shortcuts import render
from . import main
import datetime
from django.contrib import messages
from home.models import Contact

class Error(Exception):
    """Base class for other exceptions"""
    pass

class DateError(Error):
    """Raised starting date is after ending date"""
    pass
# Create your views here.
def home(request):
    if request.method == "POST":
        name=request.POST.get('name')
        email=request.POST.get('email')
        subject=request.POST.get('subject')
        message=request.POST.get('message')
        contact= Contact(name=name, email=email,subject=subject,message=message,date=datetime.datetime.today())
        contact.save()
        messages.success(request,"Your Feedback Has Been Received. Thank You!")
    return render(request, 'home.html')


def services(request):
    return render(request, 'services.html')

def search(request):
    try:
        if request.method == "POST":
            date1 = request.POST.get('start_date')
            date2 = request.POST.get('end_date')
            searched = request.POST['searched']
            # date1 = datetime.datetime.strptime(date1,"%m/%d/%Y").strftime("%Y-%m-%d")
            # date2 = datetime.datetime.strptime(date2,"%m/%d/%Y").strftime("%Y-%m-%d")
            output_data = main.search(date1,date2,searched)
            graph1=output_data[0]
            graph2=output_data[1]
            graph3=output_data[2]
            graph4=output_data[3]
            graph5=output_data[4]
            graph6=output_data[5]
            return render(request,"search.html",{"graph1":graph1,"graph2":graph2,
                "graph3":graph3,"graph4":graph4,"graph5":graph5,"graph6":graph6,
                "searched":searched})
        else:
            return render(request,"services.html")
    except KeyError:
        messages.error(request,'Something Went Wrong Or No Tweets Found Matching Your Search Query! Try Using Different Keyword')
        return render(request,'services.html')
    
def compare(request):
    try:
        if request.method == "POST":

            try:
                search1 = request.POST.get('searched1')
                search2 = request.POST.get('searched2')
                date1 = request.POST.get('start_date')
                date2 = request.POST.get('end_date')
                if search1=="":
                    raise Error
                if search2=="":
                    raise Error
                if date1=="":
                    raise Error
                if date2=="":
                    raise Error
            except Error:
                messages.error(request,'Missing Required Fields! TRY AGAIN')
                return render(request,'services.html')

            try:
                date1 = request.POST.get('start_date')
                date2 = request.POST.get('end_date')
                if date1 > date2:
                    raise DateError
            except DateError:
                messages.error(request,'End Date Should Be Greater Than Start Date! TRY AGAIN')
                return render(request,'services.html')

            date1 = request.POST.get('start_date')
            date2 = request.POST.get('end_date')
            searched1 = request.POST['searched1']
            searched2= request.POST['searched2']
            date1 = datetime.datetime.strptime(date1,"%d-%m-%Y").strftime("%Y-%m-%d")
            date2 = datetime.datetime.strptime(date2,"%d-%m-%Y").strftime("%Y-%m-%d")
            output_data = main.compare(date1,date2,searched1,searched2)
            graph1=output_data[0]
            graph2=output_data[1]
            graph3=output_data[2]
            graph4=output_data[3]
            return render(request,"compare.html",{"graph1":graph1,"graph2":graph2,
                "graph3":graph3,"graph4":graph4,
                "searched1":searched1,"searched2":searched2})
        else:
            return render(request,"services.html")
    except KeyError:
        messages.error(request,'Something Went Wrong  Or  No Tweets Found Matching Your Search Query! Try Using Different Keyword')
        return render(request,'services.html')

def map(request):
    if request.method == "POST":
        date1 = request.POST.get('start_date')
        date2 = request.POST.get('end_date')
        searched = request.POST['searched']
        lat = request.POST.get('lat')
        lng = request.POST.get('lng')
        km = request.POST.get('km')
        # date1 = datetime.datetime.strptime(date1,"%m/%d/%Y").strftime("%Y-%m-%d")
        # date2 = datetime.datetime.strptime(date2,"%m/%d/%Y").strftime("%Y-%m-%d")
        print(date1,date2,searched,lat,lng,km)
        # output_data =main.geolocation(date1,date2,searched,lat,lng,km)
        # graph1=output_data[0]
        # graph2=output_data[1]
        # graph3=output_data[2]
        # graph4=output_data[3]
        # graph5=output_data[4]
        # graph6=output_data[5]
        # print("hurray")
        # return render(request,"map.html",{"graph1":graph1,"graph2":graph2,
        #     "graph3":graph3,"graph4":graph4,"graph5":graph5,"graph6":graph6,
        #     "searched":searched})
        return render(request, 'services.html')
    else:        
        return render(request, 'services.html')

