from datetime import date
from django.shortcuts import render, redirect
from datetime import datetime, date
from . models import Reservation
from fitnessClass.models import FitnessClass
from accounts.models import *
from django.contrib.auth.decorators import login_required
from accounts.forms import *

# Create your views here.
@login_required(login_url="accounts:login")
def reserve_view(request):
    currentUser = request.user
    duplicate = False
    newUserFlag = True
    duplicateMessage = ''
    customerForm = staffCustomerForm() 
    if request.method == 'POST':
        statement = ''
        className = request.POST.get('className')
        instructorName = request.POST.get('instructorName')
        startTime = request.POST.get('startTime')
        endTime = request.POST.get('endTime')
        classDate = request.POST.get('date')
        classId = request.POST.get('classId')
        today = (date.today().strftime('%m-%d-%Y'))
        dateFormated = formatDate(classDate)        
        (available, max) = availability(classId, dateFormated)

        if int(max) >= 10:
            if int(available) >= 10:
                availabilityTitle = 'Availability'
            elif int(available) < 10 and int(available) > 0:
                availabilityTitle = 'OverDraft Room Availability'
            else:
                availabilityTitle = 'Position on WaitList'
        else:
            if int(available) < 1:
                temp_available = f'{-(available)}'
                available = temp_available
                availabilityTitle = 'Position on WaitList'
                available = (int(available) + 1)
            else:
                availabilityTitle = 'Availability'
        
        (duplicate, duplicateMessage) = checkDuplicateReservation(getCustomer(request), dateFormated, getFitnessClass(classId))
        (classPassedFlag, classPassedMessage) = checkClassPassed(getFitnessClass(classId), dateFormated)
        rv = {
            'statement': statement,
            'className':className,
            'instructorName':instructorName,
            'startTime':startTime,
            'endTime':endTime,
            'classDate':classDate ,
            'today': today,
            'availabilityTitle': availabilityTitle,
            'available':available,
            'classId':classId,
            'duplicate':duplicate,
            'duplicateMessage':duplicateMessage,
            'classPassedFlag': classPassedFlag,
            'classPassedMessage': classPassedMessage,
            'currentUser': currentUser,
            'customerForm': customerForm,
            'newUserFlag': newUserFlag,
        }
        return render(request, 'reservations/reserve.html', rv)
    else:
        return redirect('fitnessClass:schedule')


@login_required(login_url="accounts:login")
def submission_view(request):
    if request.method == "POST":
        customerReserving = None
        userExists = True
        submitted = request.POST.get('submitted')
        currentUser = request.user
        classId = request.POST.get('classId')
        classDate = request.POST.get('classDate')
        dateFormated = formatDate(classDate)
        duplicateReservation = False

        if request.user.is_staff:
            #check if customer has an account otherwise send flag that will allow them to see the create account button
            firstName = request.POST.get('firstName').lower().strip()
            lastName = request.POST.get('lastName').lower().strip()
            email = request.POST.get('email').lower().strip()
            (userExists, user) = checkUser([firstName, lastName, email])
            if userExists:
                customerReserving = user
                (flag, value) = checkDuplicateReservationStaff(classId, dateFormated, user)
                if flag == True:
                    statement = value
                    return render(request, 'reservations/submission.html', {'statement':statement, 'userExists':userExists, 'duplicateReservation':flag})        
            else:
                statement = "* User with the given information does not have an account. Please ensure all entered data is valid. Otherwise please create an account first and then create a reservation."
                return render(request, 'reservations/submission.html', {'statement':statement, 'userExists':userExists, 'duplicateReservation': duplicateReservation})        

        (available, max) = availability(classId, dateFormated)
        statement = {}
        statement['currentUser'] = currentUser
        list = FitnessClass.objects.all().filter(id = classId)

        fitnessClass = ''
        for i in list:
            fitnessClass = i
    
        reservationInstance = Reservation()
        reservationInstance.classReserved = fitnessClass
        duplicateFlag = False
        statement['duplicateFlag'] = duplicateFlag
        
        if currentUser.is_staff:
            customerId = customerReserving.id
            list = Account.objects.all().filter(id = customerId)
            customer = ''
            for i in list:
                customer = i
            reservationInstance.customerReserving = customer
        else:
            reservationInstance.customerReserving = getCustomer(request)

        if duplicateFlag == False:
            reservationInstance.classDate = dateFormated
            reservationInstance.reservationTimeStamp = datetime.now()
            statement['classDate'] = classDate
            statement['classReserved'] = reservationInstance.classReserved
            statement['customerReserving'] =  reservationInstance.customerReserving

            if int(max) > 9:
                if int(available) > 10:
                    reservationInstance.reservationStatus = 'Reserved'
                elif int(available) <= 10 and int(available) > 0:
                    reservationInstance.reservationStatus = 'OverDraft'
                else:
                    reservationInstance.reservationStatus = 'WaitList'
            else:
                if int(available) > 0:
                    reservationInstance.reservationStatus = 'Reserved'
                else:
                    reservationInstance.reservationStatus = 'WaitList'
            
            if submitted == 'True':
                reservationInstance.save()
                
            statement['reservationStatus'] = reservationInstance.reservationStatus
            waitList = getWaitListPosition(dateFormated, reservationInstance)
            statement['waitListPosition'] = 0
            if waitList > 0:
                statement['waitListPosition'] = waitList + 1
            statement['currentUser'] = currentUser
            return render(request, 'reservations/submission.html', statement)
        else:
            return render(request, 'reservations/submission.html', statement)

@login_required(login_url="accounts:login")
def myReservations_view(request):
    returnValue = []  
    if request.method == 'POST':
        reservationId = request.POST.get('reservationId')
        intId = Reservation.objects.values_list('id', flat=True).filter(id = reservationId)
        temp_id = intId[0]
        Reservation.objects.filter(id = temp_id).delete()
    currentUser = request.user.id
    customer = Account.objects.all().filter(id = currentUser)
    customerId = ''
    for i in customer:
        customerId = i
    todaysDate = date.today()
    select = Reservation.objects.all().filter(customerReserving = customerId).order_by('-classDate')

    for i in select:
        if i.classDate >= todaysDate:
            returnValue.append(i)
    return render(request, 'reservations/myReservations.html', {'reservations':returnValue})

@login_required(login_url="accounts:login")
def staffReservations_view(request):
    if request.user.is_staff == False:
        return redirect('fitnessClass:schedule')
    rv = {}
    if request.method == 'GET':
        rv['flag'] = True
        select = FitnessClass.objects.all().order_by("dayOfWeek")
        classList = {}
        days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        counter = 0
        while counter < len(days):
            for i in select:
                if i.dayOfWeek == days[counter]:
                    classList[i.id] = i
            counter += 1
        rv['classList'] = classList
        return render(request, 'reservations/staffReservations.html', rv)
    else:
        action = request.POST.get('action')
        if action == 'cancel':
            temp_id = request.POST.get('reservationId')
            Reservation.objects.filter(id = temp_id).delete()
        elif action == 'overDraftToReserved':
            temp_id = request.POST.get('reservationId')
            r = Reservation.objects.get(id = temp_id)
            r.reservationStatus = 'Reserved'
            r.save()
        elif action == 'waitListToOverDraft':
            temp_id = request.POST.get('reservationId')
            r = Reservation.objects.get(id = temp_id)
            r.reservationStatus = 'OverDraft'
            r.save()
        elif action == 'waitListToReserved':
            temp_id = request.POST.get('reservationId')
            r = Reservation.objects.get(id = temp_id)
            r.reservationStatus = 'Reserved'
            r.save()
        else:
            ''

        classId = request.POST.get('classId')
        select = Reservation.objects.all().filter(classReserved = getFitnessClass(classId)).order_by('reservationTimeStamp')
        reservedList = {}
        waitList = {}
        overDraftList = {}
        #enter code to send back the classes ID and present the staff memebers with the table 
        counter = 0
        reservedCounter = 0
        overDraftCounter = 0
        waitListCounter = 0
        cName = FitnessClass.objects.all().filter(id = classId)
        classTitle = ''
        for i in cName:
            classTitle = f'{i.className} - {i.dayOfWeek}'
        classMaximum = 0
        for i in select:
            classMaximum = i.classReserved.maximumCapacity
            (flag, value) = checkDate(i.classDate)
            if flag == True:
                counter = i.id
                if i.reservationStatus == "Reserved":
                    reservedList[counter] = i
                    rv['reservedList'] = reservedList
                    reservedCounter += 1
                elif i.reservationStatus == "WaitList":
                    waitList[counter] = i
                    rv['waitList'] = waitList
                    waitListCounter += 1
                else:
                    overDraftList[counter] = i
                    rv['overDraftList'] = overDraftList
                    overDraftCounter += 1
            else:
                rv['statement'] = value
                rv['flag'] = False
                return render(request, 'reservations/staffReservations.html', rv)
        reservedAndOverDraftTotal = reservedCounter + overDraftCounter
        rv['reservedCounter'] = reservedCounter
        rv['waitListCounter'] = waitListCounter
        rv['overDraftCounter'] = overDraftCounter
        rv['flag'] = False
        rv['classTitle'] = classTitle
        rv['classMaximum'] = int(classMaximum)
        rv['overDraftMaximum'] = 10
        rv['reservedAndOverDraftTotal'] = reservedAndOverDraftTotal
        return render(request, 'reservations/staffReservations.html', rv)

def availability(classId, date):
    count = Reservation.objects.filter(classDate = date, classReserved = classId).count()
    max = FitnessClass.objects.values_list('maximumCapacity', flat=True).get(id=classId)
    available = int(max) - count
    return (available, max)

# '01-01-2021' --> 2021-01-01
def formatDate(date):
    dateStr = date[6:] + '-' + date[0:2] + '-' + date[3:5]
    return (dateStr)

def checkDate(dateOfClass):
    temp_classDate = str(dateOfClass)
    classDate = temp_classDate[0:10]
    todayDate = date.today().strftime('%Y-%m-%d')
    if classDate < todayDate:
        return (False, 'The class date is in past')
    else:
        return (True, 'Today greater than today date')

def getCustomer(request):
    customerId = request.user.id
    list = Account.objects.all().filter(id = customerId)
    customer = ''
    for i in list:
        customer = i
    return customer

def getFitnessClass(classId):
    list = FitnessClass.objects.all().filter(id = classId)
    fitnessClass = ''
    for i in list:
        fitnessClass = i
    return fitnessClass

def getWaitListPosition(dateOfClass, currentReservation):
    list = Reservation.objects.filter(classReserved = currentReservation.classReserved, classDate = dateOfClass, reservationStatus = "WaitList")
    count = 0
    for line in list:
        resTimeStamp = line.reservationTimeStamp
        if currentReservation.reservationTimeStamp > resTimeStamp:
            count += 1
    return count

def cancelFunction(dateOfClass, currentWaitNumber):
    list = Reservation.objects.filter(classDate = dateOfClass)
    waitList = []
    id = ''
    for line in list:
        waitNumber = line.waitNumber
        if waitNumber > 0 and waitNumber < currentWaitNumber:
            tempWait = min(waitList)
            if waitNumber < tempWait:
                id = line.id
    return id

#checks for duplicate reservations when a customer is reserving
def checkDuplicateReservation(customer, dateOfClass, classId):
    count = Reservation.objects.filter(customerReserving = customer, classReserved = classId, classDate = dateOfClass).count()
    if count > 0 :
        return (True, f'* You have an existing reservation')
    else:
        return (False, '')

def checkDuplicateReservationStaff(classId, dateOfClass, customer):
    reservations = Reservation.objects.filter(classReserved = classId, classDate = dateOfClass, customerReserving = customer)
    if len(reservations) > 0:
        duplicate = None
        for i in reservations:
            duplicate = i
        return (True, f'{duplicate.customerReserving.firstName} already has a reservation made for {duplicate.classReserved.className} @ {duplicate.classReserved.startTime} on {duplicate.classReserved.dayOfWeek} - {duplicate.classDate}')
    else:
        return (False, '')

def checkClassPassed(fitnessClass, classDate):
    startTime = str(fitnessClass.startTime)
    startDate = classDate
    nT = datetime.now()
    nowTime = nT.strftime('%I:%M %p')
    nowDate = date.today().strftime('%Y-%m-%d')

    if startDate > nowDate:
        return(False, '* Class date is in the future.')
    elif startDate == nowDate:
        # same date - start time is in AM - now time is PM. Return True since class has already passed.
        if startTime[6:] == 'AM' and nowTime[6:] == 'PM':
            return(True, '* This class has begun started or has already taken place today. Can not reserve !!!')
        # same date - same half of the day i.e. (AM and AM) or (PM and PM)
        elif startTime[6:] ==  nowTime[6:]:
            # same date - same am/pm, Check hour of day and minutes
            if startTime[0:2] > nowTime[0:2]:
                return(False, '* This class startime hour is in the future')
            elif startTime[0:2] == nowTime[0:2]:
                if startTime[3:5] >= nowTime[3:5]:
                    return(False, '* Class start time minutes are greater than or equal to now time minutes')
                else:
                    return(True, '* This class has already started or has already taken place today. Can not reserve !!!')
            else:
                return(True, '* This class has already started or has already taken place today. Can not reserve !!!')
        # same date - start time is in PM - now time is in AM. Return class passed flag as false, and allow reservation.
        else:
            return(False, '* Class is later in the day')
    else:
        return(True, '* Class dates are from the past. Can not reserve !!!')

def checkUser(userInfo):
    firstName = userInfo[0].lower()
    lastName = userInfo[1].lower()
    email = userInfo[2].lower()

    account = Account.objects.all().filter(firstName = firstName, lastName = lastName, email = email)
    if len(account) > 0:
        for i in account:
            return (True, i)
    else:
        return (False, '')