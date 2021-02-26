from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import HttpResponse
from django.template.defaulttags import csrf_token
from django.views.decorators.csrf import csrf_exempt
from datetime import date, time
from .models import Login, Booked, Request, Staff, Hod_Dean, Principal, Hall, Generator_Incharge
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
from django.db.models import Q


# Create your views here.
@csrf_exempt
def login_check(request):
    print(json.loads(request.body))
    username = json.loads(request.body)['mailid']
    a = Login.objects.filter(userid=username)
    if len(a) == 0:
        return JsonResponse({'category': 'Null'})
    elif len(a) == 1:
        return JsonResponse({'category': str(a[0].category)})
    else:
        return JsonResponse({'category': 'multivalue_found'})


@csrf_exempt
def on_change_date(request):
    print(json.loads(request.body))
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
    return JsonResponse(d)


@csrf_exempt
def book_hall(request):
    print(json.loads(request.body))
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
    for i in Request.objects.filter(
            date=date(int(json.loads(request.body)['year']), int(json.loads(request.body)['month']),
                      int(json.loads(request.body)['day'])),
            hall_id=str(json.loads(request.body)['hall_id']),userid=str(json.loads(request.body)['mailid'])):
        if s_time < i.start_time and e_time < i.start_time:
            pass
        elif s_time > i.end_time and e_time > i.end_time:
            pass
        else:
            return JsonResponse({'text': 'You have already booked in this time'})
    category = json.loads(request.body)['category']
    if category == 'staff':
        t_stage = '123'
        c_stage = '1'
        ob = Staff.objects.filter(userid=json.loads(request.body)['mailid'])
        post = 'staff'
    elif category == 'hod':
        t_stage = '123'
        c_stage = '12'
        ob = Hod_Dean.objects.filter(userid=json.loads(request.body)['mailid'])
        post = 'hod'
    elif category == 'dean':
        t_stage = '123'
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
                  hall_incharge_id=h_id[0].hall_incharge_id,
                  hall_name=h_id[0].hall_name
                  )
    if json.loads(request.body)['generator_needed']=='True':
        new.generator_needed=True
        new.generator_text=json.loads(request.body)['generator_text']
        new.generator_stage = '1'
        new.chief_guest_name = json.loads(request.body)['chief_guest_name']
        new.chief_guest_detail = json.loads(request.body)['chief_guest_detail']

    new.save()
    return JsonResponse({'text': 'Request placed successfully'})

@csrf_exempt
def book_generator(request):
    br_category = json.loads(request.body)['br_category']
    if br_category=='request':
        request_id = int(json.loads(request.body)['request_id'])
        ob = Request.objects.filter(request_id=request_id)
        z = ob[0]
        z.generator_needed = True
        z.generator_text = json.loads(request.body)['generator_text']
        z.generator_stage = '1'
        z.chief_guest_name = json.loads(request.body)['chief_guest_name']
        z.chief_guest_detail = json.loads(request.body)['chief_guest_detail']
        z.save()
        return JsonResponse({'text': 'Generator Request placed successfully'})
    elif br_category=='booked':
        request_id = int(json.loads(request.body)['booking_id'])
        ob = Booked.objects.filter(request_id=request_id)
        z = ob[0]
        z.generator_needed = True
        z.generator_text = json.loads(request.body)['generator_text']
        z.generator_stage = '1'
        z.chief_guest_name = json.loads(request.body)['chief_guest_name']
        z.chief_guest_detail = json.loads(request.body)['chief_guest_detail']
        z.save()
        return JsonResponse({'text': 'Generator Request placed successfully'})
    return JsonResponse({'text': 'Generator Request failed'})


@csrf_exempt
def requests(request):
    print(json.loads(request.body))
    category = json.loads(request.body)['category']
    if category == 'hod' or category=='dean':
        ob = Hod_Dean.objects.filter(userid=json.loads(request.body)['mailid'])
        res = Request.objects.filter(user_dept=ob[0].department, user_clg=ob[0].college, current_stage='1')
        j = {'user_name': [], 'user_dept': [], 'user_clg': [], 'hall_name': [], 'function_nature': [], 'date': [],
             'start_time': [], 'end_time': [], 'additional_requirements': [], 'user_mobile': [], 'request_id': [],
             'user_designation': [],'chief_guest_name':[],'chief_guest_detail':[],'hod_notes':[],'hod_reason':[],'dean_notes':[],'dean_reason':[],
             'hall_incharge_notes':[],'hall_incharge_reason':[],'principal_notes':[],'principal_reason':[],'generator_needed':[],
             'generator_text':[],'generator_stage':[],'generator_incharge_notes':[],'generator_incharge_reason':[]}
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
            j['chief_guest_name'].append(i.chief_guest_name)
            j['chief_guest_detail'].append(i.chief_guest_detail)
            j['hod_notes'].append(i.hod_notes)
            j['hod_reason'].append(i.hod_reason)
            j['dean_notes'].append(i.dean_notes)
            j['dean_reason'].append(i.dean_reason)
            j['hall_incharge_notes'].append(i.hall_incharge_notes)
            j['hall_incharge_reason'].append(i.hall_incharge_reason)
            j['principal_notes'].append(i.principal_notes)
            j['principal_reason'].append(i.principal_reason)
            j['generator_incharge_notes'].append(i.generator_incharge_notes)
            j['generator_incharge_reason'].append(i.generator_incharge_reason)
            j['generator_needed'].append(str(i.generator_needed))
            j['generator_text'].append(i.generator_text)
            j['generator_stage'].append(i.generator_stage)



    elif category == 'hall_incharge':
        res = Request.objects.filter(current_stage='12', hall_incharge_id=json.loads(request.body)['mailid'])
        j = {'user_name': [], 'user_dept': [], 'user_clg': [], 'hall_name': [], 'function_nature': [], 'date': [],
             'start_time': [], 'end_time': [], 'additional_requirements': [], 'user_mobile': [], 'request_id': [],
             'user_designation': [],'request_id':[],'chief_guest_name':[],'chief_guest_detail':[],'hod_notes':[],'hod_reason':[],'dean_notes':[],'dean_reason':[],
             'hall_incharge_notes':[],'hall_incharge_reason':[],'principal_notes':[],'principal_reason':[],'generator_needed':[],
             'generator_text':[],'generator_stage':[],'generator_incharge_notes':[],'generator_incharge_reason':[]}
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
            j['chief_guest_name'].append(i.chief_guest_name)
            j['chief_guest_detail'].append(i.chief_guest_detail)
            j['hod_notes'].append(i.hod_notes)
            j['hod_reason'].append(i.hod_reason)
            j['dean_notes'].append(i.dean_notes)
            j['dean_reason'].append(i.dean_reason)
            j['hall_incharge_notes'].append(i.hall_incharge_notes)
            j['hall_incharge_reason'].append(i.hall_incharge_reason)
            j['principal_notes'].append(i.principal_notes)
            j['principal_reason'].append(i.principal_reason)
            j['generator_incharge_notes'].append(i.generator_incharge_notes)
            j['generator_incharge_reason'].append(i.generator_incharge_reason)
            j['generator_needed'].append(str(i.generator_needed))
            j['generator_text'].append(i.generator_text)
            j['generator_stage'].append(i.generator_stage)

    elif category == 'principal':
        ob = Principal.objects.filter(userid=json.loads(request.body)['mailid'])
        res = Request.objects.filter(user_clg=ob[0].college, current_stage='123')
        j = {'user_name': [], 'user_dept': [], 'user_clg': [], 'hall_name': [], 'function_nature': [], 'date': [],
             'start_time': [], 'end_time': [], 'additional_requirements': [], 'user_mobile': [], 'request_id': [],
             'user_designation': [],'chief_guest_name':[],'chief_guest_detail':[],'hod_notes':[],'hod_reason':[],'dean_notes':[],'dean_reason':[],
             'hall_incharge_notes':[],'hall_incharge_reason':[],'principal_notes':[],'principal_reason':[],'generator_needed':[],
             'generator_text':[],'generator_stage':[],'generator_incharge_notes':[],'generator_incharge_reason':[]}
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
            j['chief_guest_name'].append(i.chief_guest_name)
            j['chief_guest_detail'].append(i.chief_guest_detail)
            j['hod_notes'].append(i.hod_notes)
            j['hod_reason'].append(i.hod_reason)
            j['dean_notes'].append(i.dean_notes)
            j['dean_reason'].append(i.dean_reason)
            j['hall_incharge_notes'].append(i.hall_incharge_notes)
            j['hall_incharge_reason'].append(i.hall_incharge_reason)
            j['principal_notes'].append(i.principal_notes)
            j['principal_reason'].append(i.principal_reason)
            j['generator_incharge_notes'].append(i.generator_incharge_notes)
            j['generator_incharge_reason'].append(i.generator_incharge_reason)
            j['generator_needed'].append(str(i.generator_needed))
            j['generator_text'].append(i.generator_text)
            j['generator_stage'].append(i.generator_stage)
    elif category == 'generator_incharge':
        res = Request.objects.filter(generator_incharge_id=json.loads(request.body)['mailid'],generator_stage='1')
        bok = Booked.objects.filter(generator_incharge_id=json.loads(request.body)['mailid'],generator_stage='1')
        j = {'booked':{'user_name': [], 'user_dept': [], 'user_clg': [], 'hall_name': [], 'function_nature': [], 'date': [],
             'start_time': [], 'end_time': [], 'additional_requirements': [], 'user_mobile': [], 'booking_id': [],
             'user_designation': [],'chief_guest_name':[],'chief_guest_detail':[],'hod_notes':[],'hod_reason':[],'dean_notes':[],'dean_reason':[],
             'hall_incharge_notes':[],'hall_incharge_reason':[],'principal_notes':[],'principal_reason':[],'generator_needed':[],
             'generator_text':[],'generator_stage':[],'generator_incharge_notes':[],'generator_incharge_reason':[]},
             'request':{'user_name': [], 'user_dept': [], 'user_clg': [], 'hall_name': [], 'function_nature': [], 'date': [],
             'start_time': [], 'end_time': [], 'additional_requirements': [], 'user_mobile': [], 'request_id': [],
             'user_designation': [],'chief_guest_name':[],'chief_guest_detail':[],'hod_notes':[],'hod_reason':[],'dean_notes':[],'dean_reason':[],
             'hall_incharge_notes':[],'hall_incharge_reason':[],'principal_notes':[],'principal_reason':[],'generator_needed':[],
             'generator_text':[],'generator_stage':[],'generator_incharge_notes':[],'generator_incharge_reason':[]}
             }
        for i in bok:
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
            j['booked']['chief_guest_name'].append(i.chief_guest_name)
            j['booked']['chief_guest_detail'].append(i.chief_guest_detail)
            j['booked']['hod_notes'].append(i.hod_notes)
            j['booked']['hod_reason'].append(i.hod_reason)
            j['booked']['dean_notes'].append(i.dean_notes)
            j['booked']['dean_reason'].append(i.dean_reason)
            j['booked']['hall_incharge_notes'].append(i.hall_incharge_notes)
            j['booked']['hall_incharge_reason'].append(i.hall_incharge_reason)
            j['booked']['principal_notes'].append(i.principal_notes)
            j['booked']['principal_reason'].append(i.principal_reason)
            j['booked']['generator_incharge_notes'].append(i.generator_incharge_notes)
            j['booked']['generator_incharge_reason'].append(i.generator_incharge_reason)
            j['booked']['generator_needed'].append(str(i.generator_needed))
            j['booked']['generator_text'].append(i.generator_text)
            j['booked']['generator_stage'].append(i.generator_stage)
        for i in res:
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
            j['request']['chief_guest_name'].append(i.chief_guest_name)
            j['request']['chief_guest_detail'].append(i.chief_guest_detail)
            j['request']['hod_notes'].append(i.hod_notes)
            j['request']['hod_reason'].append(i.hod_reason)
            j['request']['dean_notes'].append(i.dean_notes)
            j['request']['dean_reason'].append(i.dean_reason)
            j['request']['hall_incharge_notes'].append(i.hall_incharge_notes)
            j['request']['hall_incharge_reason'].append(i.hall_incharge_reason)
            j['request']['principal_notes'].append(i.principal_notes)
            j['request']['principal_reason'].append(i.principal_reason)
            j['request']['generator_incharge_notes'].append(i.generator_incharge_notes)
            j['request']['generator_incharge_reason'].append(i.generator_incharge_reason)
            j['request']['generator_needed'].append(str(i.generator_needed))
            j['request']['generator_text'].append(i.generator_text)
            j['request']['generator_stage'].append(i.generator_stage)

    print(j)
    return JsonResponse(j)
@csrf_exempt
def decision(request):
    print(json.loads(request.body))
    category=json.loads(request.body)['category']
    if category=='hod' or category=='dean':
        request_id = int(json.loads(request.body)['request_id'])
        decision = json.loads(request.body)['decision']
        decision_note=json.loads(request.body)['decision_note']
        ob = Request.objects.filter(request_id=request_id)
        z = ob[0]
        if ob[0].current_stage=='1':
            if decision=='yes':
                z.current_stage+='2'
                if category=='hod':
                    z.hod_notes=decision_note
                elif decision=='dean':
                    z.dean_notes=decision_note
                z.save()
                return JsonResponse({'text':'successfully accepted'})
            elif decision=='no':
                z.current_stage+='c'
                if category=='hod':
                    z.hod_reason=decision_note
                elif decision=='dean':
                    z.dean_reason=decision_note
                z.save()
                return JsonResponse({'text':'successfully cancelled'})
    elif category=='hall_incharge':
        request_id = int(json.loads(request.body)['request_id'])
        decision = json.loads(request.body)['decision']
        decision_note = json.loads(request.body)['decision_note']
        ob = Request.objects.filter(request_id=request_id)
        z = ob[0]
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
                for i in Request.objects.filter(Q(current_stage='123') | Q(current_stage='1234'),
                        date=ob[0].date,
                        hall_id=ob[0].hall_id,current_stage='123'):
                    if s_time < i.start_time and e_time < i.start_time:
                        pass
                    elif s_time > i.end_time and e_time > i.end_time:
                        pass
                    else:
                        return JsonResponse({'text': 'A request already placed in this time'})
                z.current_stage+='3'
                z.hall_incharge_notes=decision_note
                z.save()
                book = Booked(request_id=ob[0].request_id, userid=ob[0].userid, user_name=ob[0].user_name,
                              user_designation=ob[0].user_designation,
                              user_mobile=ob[0].user_mobile, hall_id=ob[0].hall_id,
                              user_dept=ob[0].user_dept, user_clg=ob[0].user_clg, booking_date=ob[0].booking_date,
                              date=ob[0].date,
                              start_time=ob[0].start_time,
                              end_time=ob[0].end_time,
                              function_nature=ob[0].function_nature,
                              additional_requirements=ob[0].additional_requirements,
                              hall_incharge_id=ob[0].hall_incharge_id,
                              generator_incharge_id=ob[0].generator_incharge_id,
                              hall_name=ob[0].hall_name,
                              chief_guest_name=ob[0].chief_guest_name,
                              chief_guest_detail=ob[0].chief_guest_detail,
                              generator_needed=str(ob[0].generator_needed),
                              generator_text=ob[0].generator_text,
                              generator_stage=ob[0].generator_stage,
                              hod_notes=ob[0].hod_notes,
                              hod_reason=ob[0].hod_reason,
                              dean_notes=ob[0].dean_notes,
                              dean_reason=ob[0].dean_reason,
                              hall_incharge_notes=ob[0].hall_incharge_notes,
                              hall_incharge_reason=ob[0].hall_incharge_reason,
                              principal_notes=ob[0].principal_notes,
                              principal_reason=ob[0].principal_reason,
                              generator_incharge_notes=ob[0].generator_incharge_notes,
                              generator_incharge_reason=ob[0].generator_incharge_reason)
                book.save()
                z.delete()
                return JsonResponse({'text':'successfully accepted'})
            elif decision=='no':
                z.current_stage+='c'
                z.hall_incharge_reason = decision_note
                z.save()
                return JsonResponse({'text':'successfully cancelled'})
    elif category == 'generator_incharge':
        decision = json.loads(request.body)['decision']
        decision_note = json.loads(request.body)['decision_note']
        br_category = json.loads(request.body)['br_category']
        if br_category == 'request':
            request_id = int(json.loads(request.body)['request_id'])
            ob = Request.objects.filter(request_id=request_id)
            z = ob[0]
            if decision=='yes':
                z.generator_stage += '2'
                z.generator_incharge_notes=decision_note
                z.save()
                return JsonResponse({'text': 'successfully accepted'})
            elif decision=='no':
                z.generator_stage += 'c'
                z.generator_incharge_reason = decision_note
                z.save()
                return JsonResponse({'text': 'successfully rejected'})
        elif br_category == 'booked':
            request_id = int(json.loads(request.body)['booking_id'])
            ob = Booked.objects.filter(request_id=request_id)
            z = ob[0]
            if decision == 'yes':
                z.generator_stage += '2'
                z.generator_incharge_notes = decision_note
                z.save()
                return JsonResponse({'text': 'successfully accepted'})
            elif decision == 'no':
                z.generator_stage += 'c'
                z.generator_incharge_reason = decision_note
                z.save()
                return JsonResponse({'text': 'successfully rejected'})
    '''
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
                  hall_incharge_id=ob[0].hall_incharge_id,
                  hall_name=ob[0].hall_name,
                  hod_notes=ob[0].hod_notes,
                  hod_reason=ob[0].hod_reason,
                  dean_notes=ob[0].dean_notes,
                  dean_reason=ob[0].dean_reason,
                  hall_incharge_notes=ob[0].hall_incharge_notes,
                  hall_incharge_reason=ob[0].hall_incharge_reason,
                  principal_notes=ob[0].principal_notes,
                  principal_reason=ob[0].principal_reason
                  )
                book.save()
                z.delete()
                return JsonResponse({'text':'successfully booked'})
            elif decision=='no':
                z.current_stage+='c'
                z.save()
                return JsonResponse({'text':'successfully cancelled'})
    '''

@csrf_exempt
def mybookings(request):
    print(json.loads(request.body))
    category=json.loads(request.body)['category']
    mailid=json.loads(request.body)['mailid']
    j = {
        'booked': {'user_name': [], 'user_dept': [], 'user_clg': [], 'hall_name': [], 'function_nature': [], 'date': [],
                   'start_time': [], 'end_time': [], 'additional_requirements': [], 'user_mobile': [], 'booking_id': [],
                   'user_designation': [], 'chief_guest_name': [], 'chief_guest_detail': [], 'hod_notes': [],
                   'hod_reason': [],'dean_notes':[],'dean_reason':[],'hall_incharge_notes': [], 'hall_incharge_reason': [], 'principal_notes': [], 'principal_reason': [],
                   'generator_needed': [],'generator_text': [], 'generator_stage': [], 'generator_incharge_notes': [],
                   'generator_incharge_reason': []},
        'request': {'user_name': [], 'user_dept': [], 'user_clg': [], 'hall_name': [], 'function_nature': [],
                    'date': [],'start_time': [], 'end_time': [], 'additional_requirements': [], 'user_mobile': [],
                    'request_id': [],'user_designation': [],'total_stage':[],'current_stage':[], 'chief_guest_name': [], 'chief_guest_detail': [], 'hod_notes': [],
                    'hod_reason': [],'dean_notes':[],'dean_reason':[],'hall_incharge_notes': [], 'hall_incharge_reason': [], 'principal_notes': [],'principal_reason': [],
                    'generator_needed': [],'generator_text': [], 'generator_stage': [], 'generator_incharge_notes': [],
                    'generator_incharge_reason': []}
        }
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
        j['request']['chief_guest_name'].append(i.chief_guest_name)
        j['request']['chief_guest_detail'].append(i.chief_guest_detail)
        j['request']['hod_notes'].append(i.hod_notes)
        j['request']['hod_reason'].append(i.hod_reason)
        j['request']['dean_notes'].append(i.dean_notes)
        j['request']['dean_reason'].append(i.dean_reason)
        j['request']['hall_incharge_notes'].append(i.hall_incharge_notes)
        j['request']['hall_incharge_reason'].append(i.hall_incharge_reason)
        j['request']['principal_notes'].append(i.principal_notes)
        j['request']['principal_reason'].append(i.principal_reason)
        j['request']['generator_incharge_notes'].append(i.generator_incharge_notes)
        j['request']['generator_incharge_reason'].append(i.generator_incharge_reason)
        j['request']['generator_needed'].append(str(i.generator_needed))
        j['request']['generator_text'].append(i.generator_text)
        j['request']['generator_stage'].append(i.generator_stage)
        j['request']['total_stage'].append(i.total_stage)
        j['request']['current_stage'].append(i.current_stage)

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
        j['booked']['chief_guest_name'].append(i.chief_guest_name)
        j['booked']['chief_guest_detail'].append(i.chief_guest_detail)
        j['booked']['hod_notes'].append(i.hod_notes)
        j['booked']['hod_reason'].append(i.hod_reason)
        j['booked']['dean_notes'].append(i.dean_notes)
        j['booked']['dean_reason'].append(i.dean_reason)
        j['booked']['hall_incharge_notes'].append(i.hall_incharge_notes)
        j['booked']['hall_incharge_reason'].append(i.hall_incharge_reason)
        j['booked']['principal_notes'].append(i.principal_notes)
        j['booked']['principal_reason'].append(i.principal_reason)
        j['booked']['generator_incharge_notes'].append(i.generator_incharge_notes)
        j['booked']['generator_incharge_reason'].append(i.generator_incharge_reason)
        j['booked']['generator_needed'].append(str(i.generator_needed))
        j['booked']['generator_text'].append(i.generator_text)
        j['booked']['generator_stage'].append(i.generator_stage)
    print(j)
    return JsonResponse(j)

@csrf_exempt
def myapprovals(request):
    print(json.loads(request.body))
    j = {'booked': {'user_name': [], 'user_dept': [], 'user_clg': [], 'hall_name': [], 'function_nature': [], 'date': [],
                   'start_time': [], 'end_time': [], 'additional_requirements': [], 'user_mobile': [], 'booking_id': [],
                   'user_designation': [], 'chief_guest_name': [], 'chief_guest_detail': [], 'hod_notes': [],
                   'hod_reason': [],'dean_notes':[],'dean_reason':[], 'hall_incharge_notes': [], 'hall_incharge_reason': [], 'principal_notes': [],
                   'principal_reason': [],
                   'generator_needed': [], 'generator_text': [], 'generator_stage': [], 'generator_incharge_notes': [],
                   'generator_incharge_reason': []},
        'request': {'user_name': [], 'user_dept': [], 'user_clg': [], 'hall_name': [], 'function_nature': [],
                    'date': [], 'start_time': [], 'end_time': [], 'additional_requirements': [], 'user_mobile': [],
                    'request_id': [], 'user_designation': [], 'total_stage': [], 'current_stage': [],
                    'chief_guest_name': [], 'chief_guest_detail': [], 'hod_notes': [],
                    'hod_reason': [],'dean_notes':[],'dean_reason':[], 'hall_incharge_notes': [], 'hall_incharge_reason': [], 'principal_notes': [],
                    'principal_reason': [],
                    'generator_needed': [], 'generator_text': [], 'generator_stage': [], 'generator_incharge_notes': [],
                    'generator_incharge_reason': []}}
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
            j['request']['chief_guest_name'].append(i.chief_guest_name)
            j['request']['chief_guest_detail'].append(i.chief_guest_detail)
            j['request']['hod_notes'].append(i.hod_notes)
            j['request']['hod_reason'].append(i.hod_reason)
            j['request']['dean_notes'].append(i.dean_notes)
            j['request']['dean_reason'].append(i.dean_reason)
            j['request']['hall_incharge_notes'].append(i.hall_incharge_notes)
            j['request']['hall_incharge_reason'].append(i.hall_incharge_reason)
            j['request']['principal_notes'].append(i.principal_notes)
            j['request']['principal_reason'].append(i.principal_reason)
            j['request']['generator_incharge_notes'].append(i.generator_incharge_notes)
            j['request']['generator_incharge_reason'].append(i.generator_incharge_reason)
            j['request']['generator_needed'].append(str(i.generator_needed))
            j['request']['generator_text'].append(i.generator_text)
            j['request']['generator_stage'].append(i.generator_stage)
            j['request']['total_stage'].append(i.total_stage)
            j['request']['current_stage'].append(i.current_stage)
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
            j['booked']['chief_guest_name'].append(i.chief_guest_name)
            j['booked']['chief_guest_detail'].append(i.chief_guest_detail)
            j['booked']['hod_notes'].append(i.hod_notes)
            j['booked']['hod_reason'].append(i.hod_reason)
            j['booked']['dean_notes'].append(i.dean_notes)
            j['booked']['dean_reason'].append(i.dean_reason)
            j['booked']['hall_incharge_notes'].append(i.hall_incharge_notes)
            j['booked']['hall_incharge_reason'].append(i.hall_incharge_reason)
            j['booked']['principal_notes'].append(i.principal_notes)
            j['booked']['principal_reason'].append(i.principal_reason)
            j['booked']['generator_incharge_notes'].append(i.generator_incharge_notes)
            j['booked']['generator_incharge_reason'].append(i.generator_incharge_reason)
            j['booked']['generator_needed'].append(str(i.generator_needed))
            j['booked']['generator_text'].append(i.generator_text)
            j['booked']['generator_stage'].append(i.generator_stage)
    elif category=='hall_incharge':
        for i in Request.objects.filter(Q(current_stage='123') | Q(current_stage='12c'),Q(hall_incharge_id=mailid)).order_by('-date'):
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
            j['request']['chief_guest_name'].append(i.chief_guest_name)
            j['request']['chief_guest_detail'].append(i.chief_guest_detail)
            j['request']['hod_notes'].append(i.hod_notes)
            j['request']['hod_reason'].append(i.hod_reason)
            j['request']['dean_notes'].append(i.dean_notes)
            j['request']['dean_reason'].append(i.dean_reason)
            j['request']['hall_incharge_notes'].append(i.hall_incharge_notes)
            j['request']['hall_incharge_reason'].append(i.hall_incharge_reason)
            j['request']['principal_notes'].append(i.principal_notes)
            j['request']['principal_reason'].append(i.principal_reason)
            j['request']['generator_incharge_notes'].append(i.generator_incharge_notes)
            j['request']['generator_incharge_reason'].append(i.generator_incharge_reason)
            j['request']['generator_needed'].append(str(i.generator_needed))
            j['request']['generator_text'].append(i.generator_text)
            j['request']['generator_stage'].append(i.generator_stage)
            j['request']['total_stage'].append(i.total_stage)
            j['request']['current_stage'].append(i.current_stage)
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
            j['booked']['chief_guest_name'].append(i.chief_guest_name)
            j['booked']['chief_guest_detail'].append(i.chief_guest_detail)
            j['booked']['hod_notes'].append(i.hod_notes)
            j['booked']['hod_reason'].append(i.hod_reason)
            j['booked']['dean_notes'].append(i.dean_notes)
            j['booked']['dean_reason'].append(i.dean_reason)
            j['booked']['hall_incharge_notes'].append(i.hall_incharge_notes)
            j['booked']['hall_incharge_reason'].append(i.hall_incharge_reason)
            j['booked']['principal_notes'].append(i.principal_notes)
            j['booked']['principal_reason'].append(i.principal_reason)
            j['booked']['generator_incharge_notes'].append(i.generator_incharge_notes)
            j['booked']['generator_incharge_reason'].append(i.generator_incharge_reason)
            j['booked']['generator_needed'].append(str(i.generator_needed))
            j['booked']['generator_text'].append(i.generator_text)
            j['booked']['generator_stage'].append(i.generator_stage)
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
            j['request']['chief_guest_name'].append(i.chief_guest_name)
            j['request']['chief_guest_detail'].append(i.chief_guest_detail)
            j['request']['hod_notes'].append(i.hod_notes)
            j['request']['hod_reason'].append(i.hod_reason)
            j['request']['dean_notes'].append(i.dean_notes)
            j['request']['dean_reason'].append(i.dean_reason)
            j['request']['hall_incharge_notes'].append(i.hall_incharge_notes)
            j['request']['hall_incharge_reason'].append(i.hall_incharge_reason)
            j['request']['principal_notes'].append(i.principal_notes)
            j['request']['principal_reason'].append(i.principal_reason)
            j['request']['generator_incharge_notes'].append(i.generator_incharge_notes)
            j['request']['generator_incharge_reason'].append(i.generator_incharge_reason)
            j['request']['generator_needed'].append(str(i.generator_needed))
            j['request']['generator_text'].append(i.generator_text)
            j['request']['generator_stage'].append(i.generator_stage)
            j['request']['total_stage'].append(i.total_stage)
            j['request']['current_stage'].append(i.current_stage)
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
            j['booked']['chief_guest_name'].append(i.chief_guest_name)
            j['booked']['chief_guest_detail'].append(i.chief_guest_detail)
            j['booked']['hod_notes'].append(i.hod_notes)
            j['booked']['hod_reason'].append(i.hod_reason)
            j['booked']['dean_notes'].append(i.dean_notes)
            j['booked']['dean_reason'].append(i.dean_reason)
            j['booked']['hall_incharge_notes'].append(i.hall_incharge_notes)
            j['booked']['hall_incharge_reason'].append(i.hall_incharge_reason)
            j['booked']['principal_notes'].append(i.principal_notes)
            j['booked']['principal_reason'].append(i.principal_reason)
            j['booked']['generator_incharge_notes'].append(i.generator_incharge_notes)
            j['booked']['generator_incharge_reason'].append(i.generator_incharge_reason)
            j['booked']['generator_needed'].append(str(i.generator_needed))
            j['booked']['generator_text'].append(i.generator_text)
            j['booked']['generator_stage'].append(i.generator_stage)
    elif category=='generator_incharge':
        for i in Request.objects.filter(Q(generator_stage='12') | Q(generator_stage='1c'),Q(generator_incharge_id=mailid)).order_by('-date'):
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
            j['request']['chief_guest_name'].append(i.chief_guest_name)
            j['request']['chief_guest_detail'].append(i.chief_guest_detail)
            j['request']['hod_notes'].append(i.hod_notes)
            j['request']['hod_reason'].append(i.hod_reason)
            j['request']['dean_notes'].append(i.dean_notes)
            j['request']['dean_reason'].append(i.dean_reason)
            j['request']['hall_incharge_notes'].append(i.hall_incharge_notes)
            j['request']['hall_incharge_reason'].append(i.hall_incharge_reason)
            j['request']['principal_notes'].append(i.principal_notes)
            j['request']['principal_reason'].append(i.principal_reason)
            j['request']['generator_incharge_notes'].append(i.generator_incharge_notes)
            j['request']['generator_incharge_reason'].append(i.generator_incharge_reason)
            j['request']['generator_needed'].append(str(i.generator_needed))
            j['request']['generator_text'].append(i.generator_text)
            j['request']['generator_stage'].append(i.generator_stage)
            j['request']['total_stage'].append(i.total_stage)
            j['request']['current_stage'].append(i.current_stage)
        for i in Booked.objects.filter(Q(generator_stage='12') | Q(generator_stage='1c'),Q(generator_incharge_id=mailid)).order_by('-date'):
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
            j['booked']['chief_guest_name'].append(i.chief_guest_name)
            j['booked']['chief_guest_detail'].append(i.chief_guest_detail)
            j['booked']['hod_notes'].append(i.hod_notes)
            j['booked']['hod_reason'].append(i.hod_reason)
            j['booked']['dean_notes'].append(i.dean_notes)
            j['booked']['dean_reason'].append(i.dean_reason)
            j['booked']['hall_incharge_notes'].append(i.hall_incharge_notes)
            j['booked']['hall_incharge_reason'].append(i.hall_incharge_reason)
            j['booked']['principal_notes'].append(i.principal_notes)
            j['booked']['principal_reason'].append(i.principal_reason)
            j['booked']['generator_incharge_notes'].append(i.generator_incharge_notes)
            j['booked']['generator_incharge_reason'].append(i.generator_incharge_reason)
            j['booked']['generator_needed'].append(str(i.generator_needed))
            j['booked']['generator_text'].append(i.generator_text)
            j['booked']['generator_stage'].append(i.generator_stage)
    print(j)
    return JsonResponse(j)

@csrf_exempt
def cancel(request):
    print(json.loads(request.body))
    category = json.loads(request.body)['category']
    mailid = json.loads(request.body)['mailid']
    id = json.loads(request.body)['id']
    c_category=json.loads(request.body)['cancel_category']
    if c_category=='request':
        ob = Request.objects.filter(request_id=id)
        if category == "staff" and ob[0].current_stage=='1':
            Request.objects.filter(request_id=id).delete()
            return JsonResponse({'text':'successfully cancelled'})
        elif category == "hod" or category == "dean" and ob[0].current_stage=='12':
            Request.objects.filter(request_id=id).delete()
            return JsonResponse({'text':'successfully cancelled'})

    if c_category=='booked':
        if category=="hall_incharge":
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


@csrf_exempt
def mobile_auth(request):
    return render(request,"mobile_auth.html")