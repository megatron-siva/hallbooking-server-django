from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import HttpResponse
from django.template.defaulttags import csrf_token
from django.views.decorators.csrf import csrf_exempt
from datetime import date, time
from .models import Login, Booked, Request, Staff, Hod_Dean, Principal, Hall
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json


# Create your views here.
@csrf_exempt
def login_check(request):
    username = json.loads(request.body)['mailid']
    a = Login.objects.filter(userid=username)
    if len(a) == 0:
        return JsonResponse({'category': 'Null'})
    elif len(a) == 1:
        print(str(a[0].category))
        return JsonResponse({'category': str(a[0].category)})
    else:
        return JsonResponse({'category': 'multivalue_found'})


@csrf_exempt
def on_change_date(request):
    d = {}
    for j in Hall.objects.all():
        d[str(j.hall_id)]=[]
    for i in Booked.objects.filter(
            date=date(int(json.loads(request.body)['year']), int(json.loads(request.body)['month']),
                      int(json.loads(request.body)['day']))):
        if len(d[str(i.hall_id)])==0:
            d[str(i.hall_id)].extend(['1', str(i.start_time) + ' - ' + str(i.end_time)])
        else:
            d[str(i.hall_id)][1] +='\n'+str(i.start_time) + ' - ' + str(i.end_time)
            d[str(i.hall_id)][0] = str(int(d[str(i.hall_id)][0]) + 1)
    print(int(json.loads(request.body)['year']), int(json.loads(request.body)['month']),
                      int(json.loads(request.body)['day']))
    return JsonResponse(d)


@csrf_exempt
def book_hall(request):
    s_time = time(int(json.loads(request.body)['s_hour']), int(json.loads(request.body)['s_minute']),
                  )
    e_time = time(int(json.loads(request.body)['e_hour']), int(json.loads(request.body)['e_minute']),
                  )
    for i in Booked.objects.filter(
            date=date(int(json.loads(request.body)['year']), int(json.loads(request.body)['month']),
                      int(json.loads(request.body)['day'])),
            hall_id=str(json.loads(request.body)['hall_id'])):
        if s_time < i.start_time and e_time < i.start_time:
            pass
        elif s_time > i.end_time and e_time > i.end_time:
            pass
        else:
            return JsonResponse({'text': 'Already booked in this time'})
    category = json.loads(request.body)['category']
    if category == 'staff':
        t_stage = '1234'
        c_stage = '1'
        ob = Staff.objects.filter(userid=json.loads(request.body)['mailid'])
        post = 'staff'
    elif category == 'hod':
        t_stage = '1234'
        c_stage = '12'
        ob = Hod_Dean.objects.filter(userid=json.loads(request.body)['mailid'])
        post = 'hod'
    elif category == 'dean':
        t_stage = '1234'
        c_stage = '12'
        ob = Hod_Dean.objects.filter(userid=json.loads(request.body)['mailid'])
        post = 'dean'
    if json.loads(request.body)['additional_requirements']==None:
        requirement='Nothing'
    else:
        requirement=json.loads(request.body)['additional_requirements']
    h_id = Hall.objects.filter(hall_id=json.loads(request.body)['hall_id'])
    new = Request(userid=str(json.loads(request.body)['mailid']), user_name=ob[0].name, user_designation=post,
                  user_mobile=json.loads(request.body)['mobile'], hall_id=json.loads(request.body)['hall_id'],
                  total_stage=t_stage,
                  current_stage=c_stage, user_dept=ob[0].department, user_clg=ob[0].college, booking_date=date.today(),
                  date=date(int(json.loads(request.body)['year']),int(json.loads(request.body)['month']), int(json.loads(request.body)['day'])),
                  start_time=time(int(json.loads(request.body)['s_hour']), int(json.loads(request.body)['s_minute'])),
                  end_time=time(int(json.loads(request.body)['e_hour']), int(json.loads(request.body)['e_minute'])),
                  function_nature=json.loads(request.body)['function_nature'],
                  additional_requirements=requirement,
                  hall_incharge_id=h_id[0].hall_incharge_id, hall_name=h_id[0].hall_name)
    new.save()
    return JsonResponse({'text': 'request placed successfully'})

@csrf_exempt
def requests(request):
    category = json.loads(request.body)['category']
    if category == 'hod' or category=='dean':
        ob = Hod_Dean.objects.filter(userid=json.loads(request.body)['mailid'])
        res = Request.objects.filter(user_dept=ob[0].department, user_clg=ob[0].college, current_stage='1')
        j = {'user_name': [], 'user_dept': [], 'user_clg': [], 'hall_name': [], 'function_nature': [], 'date': [],
             'start_time': [], 'end_time': [], 'additional_requirements': [], 'user_mobile': [], 'request_id': [],
             'user_designation': []}
        for i in res:
            j['user_name'].append(i.user_name)
            j['user_dept'].append(i.user_dept)
            j['user_clg'].append(i.user_clg)
            j['hall_name'].append(i.hall_name)
            j['function_nature'].append(i.function_nature)
            j['date'].append(str(i.date))
            j['start_time'].append(str(i.start_time))
            j['end_time'].append(str(i.end_time))
            j['additional_requirements'].append(i.additional_requirements)
            j['user_mobile'].append(i.user_mobile)
            j['request_id'].append(str(i.request_id))
            j['user_designation'].append(i.user_designation)

        return JsonResponse(j)

    elif category == 'hall_incharge':
        res = Request.objects.filter(current_stage='12', hall_incharge_id=json.loads(request.body)['mailid'])
        j = {'user_name': [], 'user_dept': [], 'user_clg': [], 'hall_name': [], 'function_nature': [], 'date': [],
             'start_time': [], 'end_time': [], 'additional_requirements': [], 'user_mobile': [], 'request_id': [],
             'user_designation': []}
        for i in res:
            j['user_name'].append(i.user_name)
            j['user_dept'].append(i.user_dept)
            j['user_clg'].append(i.user_clg)
            j['hall_name'].append(i.hall_name)
            j['function_nature'].append(i.function_nature)
            j['date'].append(str(i.date))
            j['start_time'].append(str(i.start_time))
            j['end_time'].append(str(i.end_time))
            j['additional_requirements'].append(i.additional_requirements)
            j['user_mobile'].append(i.user_mobile)
            j['request_id'].append(str(i.request_id))
            j['user_designation'].append(i.user_designation)
        return JsonResponse(j)
    elif category == 'principal':
        ob = Principal.objects.filter(userid=json.loads(request.body)['mailid'])
        res = Request.objects.filter(user_clg=ob[0].college, current_stage='123')
        j = {'user_name': [], 'user_dept': [], 'user_clg': [], 'hall_name': [], 'function_nature': [], 'date': [],
             'start_time': [], 'end_time': [], 'additional_requirements': [], 'user_mobile': [], 'request_id': [],
             'user_designation': []}
        for i in res:
            j['user_name'].append(i.user_name)
            j['user_dept'].append(i.user_dept)
            j['user_clg'].append(i.user_clg)
            j['hall_name'].append(i.hall_name)
            j['function_nature'].append(i.function_nature)
            j['date'].append(str(i.date))
            j['start_time'].append(str(i.start_time))
            j['end_time'].append(str(i.end_time))
            j['additional_requirements'].append(i.additional_requirements)
            j['user_mobile'].append(i.user_mobile)
            j['request_id'].append(str(i.request_id))
            j['user_designation'].append(i.user_designation)
        return JsonResponse(j)
@csrf_exempt
def decision(request):
    request_id=int(json.loads(request.body)['request_id'])
    category=json.loads(request.body)['category']
    decision=json.loads(request.body)['decision']
    ob=Request.objects.filter(request_id=request_id)
    z=ob[0]
    if category=='hod' or category=='dean':
        if ob[0].current_stage=='1':
            if decision=='yes':
                z.current_stage+='2'
                z.save()
                return JsonResponse({'text':'successfully accepted'})
            elif decision=='no':
                z.current_stage+='c'
                z.save()
                return JsonResponse({'text':'successfully cancelled'})
    elif category=='hall_incharge':
        if ob[0].current_stage=='12':
            if decision=='yes':
                s_time = ob[0].start_time
                e_time = ob[0].end_time
                for i in Booked.objects.filter(
                        date=ob[0].date,
                        hall_id=ob[0].hall_id):
                    if s_time < i.start_time and e_time < i.start_time:
                        pass
                    elif s_time > i.end_time and e_time > i.end_time:
                        pass
                    else:
                        return JsonResponse({'text': 'Already booked in this time'})
                for i in Request.objects.filter(
                        date=ob[0].date,
                        hall_id=ob[0].hall_id):
                    if s_time < i.start_time and e_time < i.start_time:
                        pass
                    elif s_time > i.end_time and e_time > i.end_time:
                        pass
                    else:
                        return JsonResponse({'text': 'A request already placed in this time'})
                z.current_stage+='3'
                z.save()
                return JsonResponse({'text':'successfully accepted'})
            elif decision=='no':
                z.current_stage+='c'
                z.save()
                return JsonResponse({'text':'successfully cancelled'})
    elif category=='principal':
        if ob[0].current_stage=='123':
            if decision=='yes':
                s_time=ob[0].start_time
                e_time=ob[0].end_time
                for i in Booked.objects.filter(
                        date=ob[0].date,
                        hall_id=ob[0].hall_id):
                    if s_time < i.start_time and e_time < i.start_time:
                        pass
                    elif s_time > i.end_time and e_time > i.end_time:
                        pass
                    else:
                        return JsonResponse({'text': 'Already booked in this time'})
                z.current_stage+='4'
                z.save()
                book=Booked(request_id=ob[0].request_id,userid=ob[0].userid, user_name=ob[0].user_name, user_designation=ob[0].user_designation,
                  user_mobile=ob[0].user_mobile, hall_id=ob[0].hall_id,
                  user_dept=ob[0].user_dept, user_clg=ob[0].user_clg, booking_date=ob[0].booking_date,
                  date=ob[0].date,
                  start_time=ob[0].start_time,
                  end_time=ob[0].end_time,
                  function_nature=ob[0].function_nature,
                  additional_requirements=ob[0].additional_requirements,
                  hall_incharge_id=ob[0].hall_incharge_id, hall_name=ob[0].hall_name)
                book.save()
                z.delete()
                return JsonResponse({'text':'successfully booked'})
            elif decision=='no':
                z.current_stage+='c'
                z.save()
                return JsonResponse({'text':'successfully cancelled'})

@csrf_exempt
def mybookings(request):
    category=json.loads(request.body)['category']
    mailid=json.loads(request.body)['mailid']
    j = {'request':{'user_name': [], 'user_dept': [], 'user_clg': [], 'hall_name': [], 'function_nature': [], 'date': [],
         'start_time': [], 'end_time': [], 'additional_requirements': [], 'user_mobile': [], 'request_id': [],
         'user_designation': [],'total_stage':[],'current_stage':[]},
         'booked':{'user_name': [], 'user_dept': [], 'user_clg': [], 'hall_name': [], 'function_nature': [], 'date': [],
         'start_time': [], 'end_time': [], 'additional_requirements': [], 'user_mobile': [], 'booking_id': [],
         'user_designation': []}}
    for i in Request.objects.filter(userid=mailid).order_by('-date'):
        j['request']['user_name'].append(i.user_name)
        j['request']['user_dept'].append(i.user_dept)
        j['request']['user_clg'].append(i.user_clg)
        j['request']['hall_name'].append(i.hall_name)
        j['request']['function_nature'].append(i.function_nature)
        j['request']['date'].append(str(i.date))
        j['request']['start_time'].append(str(i.start_time))
        j['request']['end_time'].append(str(i.end_time))
        j['request']['additional_requirements'].append(i.additional_requirements)
        j['request']['user_mobile'].append(i.user_mobile)
        j['request']['request_id'].append(str(i.request_id))
        j['request']['user_designation'].append(i.user_designation)
        j['request']['current_stage'].append(i.current_stage)
        j['request']['total_stage'].append(i.total_stage)

    for i in Booked.objects.filter(userid=mailid).order_by('-date'):
        j['booked']['user_name'].append(i.user_name)
        j['booked']['user_dept'].append(i.user_dept)
        j['booked']['user_clg'].append(i.user_clg)
        j['booked']['hall_name'].append(i.hall_name)
        j['booked']['function_nature'].append(i.function_nature)
        j['booked']['date'].append(str(i.date))
        j['booked']['start_time'].append(str(i.start_time))
        j['booked']['end_time'].append(str(i.end_time))
        j['booked']['additional_requirements'].append(i.additional_requirements)
        j['booked']['user_mobile'].append(i.user_mobile)
        j['booked']['booking_id'].append(str(i.booking_id))
        j['booked']['user_designation'].append(i.user_designation)
    return JsonResponse(j)

@csrf_exempt
def myapprovals(request):
    j = {'request': {'user_name': [], 'user_dept': [], 'user_clg': [], 'hall_name': [], 'function_nature': [],
                     'date': [],
                     'start_time': [], 'end_time': [], 'additional_requirements': [], 'user_mobile': [],
                     'request_id': [],
                     'user_designation': [], 'total_stage': [], 'current_stage': []},
         'booked': {'user_name': [], 'user_dept': [], 'user_clg': [], 'hall_name': [], 'function_nature': [],
                    'date': [],
                    'start_time': [], 'end_time': [], 'additional_requirements': [], 'user_mobile': [],
                    'booking_id': [],
                    'user_designation': []}}
    category = json.loads(request.body)['category']
    mailid = json.loads(request.body)['mailid']
    if category=='hod' or category== 'dean':
        u_deatils=Hod_Dean.objects.filter(userid=mailid)
        for i in Request.objects.filter(user_dept=u_deatils[0].department,user_clg=u_deatils[0].college).exclude(userid=mailid).exclude(current_stage='1').order_by('-date'):
            j['request']['user_name'].append(i.user_name)
            j['request']['user_dept'].append(i.user_dept)
            j['request']['user_clg'].append(i.user_clg)
            j['request']['hall_name'].append(i.hall_name)
            j['request']['function_nature'].append(i.function_nature)
            j['request']['date'].append(str(i.date))
            j['request']['start_time'].append(str(i.start_time))
            j['request']['end_time'].append(str(i.end_time))
            j['request']['additional_requirements'].append(i.additional_requirements)
            j['request']['user_mobile'].append(i.user_mobile)
            j['request']['request_id'].append(str(i.request_id))
            j['request']['user_designation'].append(i.user_designation)
            j['request']['current_stage'].append(i.current_stage)
            j['request']['total_stage'].append(i.total_stage)
        for i in Booked.objects.filter(user_dept=u_deatils[0].department,user_clg=u_deatils[0].college).exclude(userid=mailid).order_by('-date'):
            j['booked']['user_name'].append(i.user_name)
            j['booked']['user_dept'].append(i.user_dept)
            j['booked']['user_clg'].append(i.user_clg)
            j['booked']['hall_name'].append(i.hall_name)
            j['booked']['function_nature'].append(i.function_nature)
            j['booked']['date'].append(str(i.date))
            j['booked']['start_time'].append(str(i.start_time))
            j['booked']['end_time'].append(str(i.end_time))
            j['booked']['additional_requirements'].append(i.additional_requirements)
            j['booked']['user_mobile'].append(i.user_mobile)
            j['booked']['booking_id'].append(str(i.booking_id))
            j['booked']['user_designation'].append(i.user_designation)
    elif category=='hall_incharge':
        for i in Request.objects.filter(hall_incharge_id=mailid,current_stage='123'or'12c').order_by('-date'):
            j['request']['user_name'].append(i.user_name)
            j['request']['user_dept'].append(i.user_dept)
            j['request']['user_clg'].append(i.user_clg)
            j['request']['hall_name'].append(i.hall_name)
            j['request']['function_nature'].append(i.function_nature)
            j['request']['date'].append(str(i.date))
            j['request']['start_time'].append(str(i.start_time))
            j['request']['end_time'].append(str(i.end_time))
            j['request']['additional_requirements'].append(i.additional_requirements)
            j['request']['user_mobile'].append(i.user_mobile)
            j['request']['request_id'].append(str(i.request_id))
            j['request']['user_designation'].append(i.user_designation)
        for i in Booked.objects.filter(hall_incharge_id=mailid).order_by('-date'):
            j['booked']['user_name'].append(i.user_name)
            j['booked']['user_dept'].append(i.user_dept)
            j['booked']['user_clg'].append(i.user_clg)
            j['booked']['hall_name'].append(i.hall_name)
            j['booked']['function_nature'].append(i.function_nature)
            j['booked']['date'].append(str(i.date))
            j['booked']['start_time'].append(str(i.start_time))
            j['booked']['end_time'].append(str(i.end_time))
            j['booked']['additional_requirements'].append(i.additional_requirements)
            j['booked']['user_mobile'].append(i.user_mobile)
            j['booked']['booking_id'].append(str(i.booking_id))
            j['booked']['user_designation'].append(i.user_designation)
    elif category=='principal':
        u_deatils = Principal.objects.filter(userid=mailid)
        for i in Request.objects.filter(user_clg=u_deatils[0].college,current_stage='123c').order_by('-date'):
            j['request']['user_name'].append(i.user_name)
            j['request']['user_dept'].append(i.user_dept)
            j['request']['user_clg'].append(i.user_clg)
            j['request']['hall_name'].append(i.hall_name)
            j['request']['function_nature'].append(i.function_nature)
            j['request']['date'].append(str(i.date))
            j['request']['start_time'].append(str(i.start_time))
            j['request']['end_time'].append(str(i.end_time))
            j['request']['additional_requirements'].append(i.additional_requirements)
            j['request']['user_mobile'].append(i.user_mobile)
            j['request']['request_id'].append(str(i.request_id))
            j['request']['user_designation'].append(i.user_designation)
        for i in Booked.objects.filter(user_clg=u_deatils[0].college).order_by('-date'):
            j['booked']['user_name'].append(i.user_name)
            j['booked']['user_dept'].append(i.user_dept)
            j['booked']['user_clg'].append(i.user_clg)
            j['booked']['hall_name'].append(i.hall_name)
            j['booked']['function_nature'].append(i.function_nature)
            j['booked']['date'].append(str(i.date))
            j['booked']['start_time'].append(str(i.start_time))
            j['booked']['end_time'].append(str(i.end_time))
            j['booked']['additional_requirements'].append(i.additional_requirements)
            j['booked']['user_mobile'].append(i.user_mobile)
            j['booked']['booking_id'].append(str(i.booking_id))
            j['booked']['user_designation'].append(i.user_designation)

    return JsonResponse(j)

@csrf_exempt
def cancel(request):
    c_category=json.loads(request.body)['cancel_category']
    if c_category=='request':
        id=json.loads(request.body)['id']
        Request.objects.filter(request_id=id).delete()
        return JsonResponse({'text':'successfully cancelled'})

    if c_category=='booked':
        id=json.loads(request.body)['id']
        Booked.objects.filter(booking_id=id).delete()
        return JsonResponse({'text':'successfully cancelled'})
    return JsonResponse({'text':'cancellation unsuccessful'})
def register(request):
    return HttpResponse('HELLO MEGATRON.')


def mail(send_to_email, subject, message):
    email = 'suryaprakask.18cs100@nandhaengg.org'
    password = 'neccse2018'

    msg = MIMEMultipart()
    msg['From'] = email
    msg['To'] = send_to_email
    msg['Subject'] = subject

    # Attach the message to the MIMEMultipart object
    msg.attach(MIMEText(message, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(email, password)
    text = msg.as_string()  # You now need to convert the MIMEMultipart object to a string to send
    server.sendmail(email, send_to_email, text)
    server.quit()

