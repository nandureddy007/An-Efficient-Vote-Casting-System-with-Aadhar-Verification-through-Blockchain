from django.shortcuts import render
from django.template import RequestContext
from django.contrib import messages
from django.http import HttpResponse
from django.conf import settings
import os
import json
from web3 import Web3, HTTPProvider
from django.core.files.storage import FileSystemStorage
from datetime import date
import FingerMatch
import timeit
import matplotlib.pyplot as plt
import io
import base64

global username, otp
global contract, web3
global usersList, partyList, voteList
latency = [5, 9, 7, 12]

def Graph(request):
    if request.method == 'GET':
        global latency
        print(latency)
        num = []
        for i in range(len(latency)):
            num.append((i+1))
        plt.plot(num, latency, label='Latency')
        plt.xlabel("Number of Transactions")
        plt.ylabel("Latency")
        plt.title("Blockchain Latency Graph")
        plt.legend()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        plt.close()
        img_b64 = base64.b64encode(buf.getvalue()).decode()    
        context= {'data':'Blockchain Latency Graph', 'img': img_b64}
        return render(request, 'UserScreen.html', context)   

#function to call contract
def getContract():
    global contract, web3
    blockchain_address = 'http://127.0.0.1:9545'
    web3 = Web3(HTTPProvider(blockchain_address))
    web3.eth.defaultAccount = web3.eth.accounts[0]
    compiled_contract_path = 'Voting.json' #voting contract file
    deployed_contract_address = '0xBDC58Bb54089145C9768ddcdaEE301D9b5F53e41' #contract address
    with open(compiled_contract_path) as file:
        contract_json = json.load(file)  # load contract info as JSON
        contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions
    file.close()
    contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
getContract()

def getUsersList():
    global usersList, contract
    usersList = []
    count = contract.functions.getUserCount().call()
    for i in range(0, count):
        user = contract.functions.getUsername(i).call()
        password = contract.functions.getPassword(i).call()
        email = contract.functions.getEmail(i).call()
        aadhar_finger = contract.functions.getAadharFinger(i).call()
        usersList.append([user, password, email, aadhar_finger])

def getPartyList():
    global partyList, contract
    partyList = []
    count = contract.functions.getPartyCount().call()
    for i in range(0, count):
        cname = contract.functions.getCandidateName(i).call()
        pname = contract.functions.getPartyName(i).call()
        area = contract.functions.getArea(i).call()
        symbol = contract.functions.getSymbol(i).call()
        partyList.append([cname, pname, area, symbol])

def getVoteList():
    global voteList, contract
    voteList = []
    count = contract.functions.getVotingCount().call()
    for i in range(0, count):
        user = contract.functions.getUser(i).call()
        party = contract.functions.getParty(i).call()
        dd = contract.functions.getDate(i).call()
        candidate = contract.functions.getCandidate(i).call()
        voteList.append([user, party, dd, candidate])

getUsersList()
getPartyList()        
getVoteList()        

def alreadyCastVote(candidate):
    global voteList
    count = 0
    for i in range(len(voteList)):
        vl = voteList[i]
        if vl[0] == candidate:
            count = 1
    return count

def FinishVote(request):
    if request.method == 'GET':
        global username, voteList
        cname = request.GET.get('cname', False)
        pname = request.GET.get('pname', False)
        voter = ''
        today = date.today()
        status = 'Your vote casted to '+cname
        msg = contract.functions.createVote(username, pname, str(today), cname).transact()
        web3.eth.waitForTransactionReceipt(msg)
        voteList.append([username, pname, str(today), cname])
        context= {'data':'<font size=3 color=white>Your Vote Accepted for Candidate '+cname}
        return render(request, 'UserScreen.html', context)

def getOutput():
    global partyList
    output = '<table border=1 align=center>'
    output+='<tr><th><font size=3 color=white>Candidate Name</font></th>'
    output+='<th><font size=3 color=white>Party Name</font></th>'
    output+='<th><font size=3 color=white>Area Name</font></th>'
    output+='<th><font size=3 color=white>Image</font></th>'
    output+='<th><font size=3 color=white>Cast Vote Here</font></th></tr>'
    for i in range(len(partyList)):
        pl = partyList[i]
        output+='<tr><td><font size=3 color=white>'+pl[0]+'</font></td>'
        output+='<td><font size=3 color=white>'+pl[1]+'</font></td>'
        output+='<td><font size=3 color=white>'+pl[2]+'</font></td>'
        output+='<td><img src="/static/parties/'+pl[3]+'" width=200 height=200></img></td>'
        output+='<td><a href="FinishVote?cname='+pl[0]+'&pname='+pl[1]+'"><font size=3 color=white>Click Here</font></a></td></tr>'
    output+="</table><br/><br/><br/><br/><br/><br/>"        
    return output

def Vote(request):
    if request.method == 'GET':
        global username
        dd = ""
        status = ""
        page = 'Vote.html'
        if os.path.exists("VotingApp/static/dd.txt"):
            with open("VotingApp/static/dd.txt", "rb") as file:
                value = file.read()
            file.close()
            dd = value.decode()
            arr = dd.split(" ")
            arr = arr[0]
            arr = arr.split("-")
            if len(arr[1].strip()) == 1:
                arr[1] = "0"+arr[1].strip()
            if len(arr[0].strip()) == 1:
                arr[0] = "0"+arr[0].strip()
            print(arr)    
            today = str(date.today())
            current_arr = today.split("-")
            print(current_arr)
            if current_arr[0] == arr[0] and current_arr[1] == arr[1] and current_arr[2] == arr[2]:
                count = alreadyCastVote(username)
                if count == 0:
                    status = getOutput()
                else:
                    status = "You already casted vote"
            else:
                status = "Today is not an election date.<br/>Election is on "+dd
                
        else:
            status = "Election date not yet publish.<br/>Election date you can see in your home page after login"
        context= {'data':status}
        return render(request, page, context)         
        

def getVoteCount(cname, pname):
    global voteList
    count = 0
    for i in range(len(voteList)):
        vl = voteList[i]
        if vl[1] == pname and vl[3] == cname:
            count += 1
    return count        

def ViewCount(request):
    if request.method == 'GET':
        output = '<table border=1 align=center>'
        output+='<tr><th><font size=3 color=white>Candidate Name</font></th>'
        output+='<th><font size=3 color=white>Party Name</font></th>'
        output+='<th><font size=3 color=white>Area Name</font></th>'
        output+='<th><font size=3 color=white>Image</font></th>'
        output+='<th><font size=3 color=white>Vote Count</font></th>'
        for i in range(len(partyList)):
            pl = partyList[i]
            count = getVoteCount(pl[0], pl[1])
            output+='<tr><td><font size=3 color=white>'+pl[0]+'</font></td>'
            output+='<td><font size=3 color=white>'+pl[1]+'</font></td>'
            output+='<td><font size=3 color=white>'+pl[2]+'</font></td>'
            output+='<td><img src="/static/parties/'+pl[3]+'" width=200 height=200></img></td>'
            output+='<td><font size=3 color=white>'+str(count)+'</font></td></tr>'
        output+="</table><br/><br/><br/><br/><br/><br/>"        
        context= {'data':output}
        return render(request, 'ViewResult.html', context)

def ViewUserResult(request):
    if request.method == 'GET':
        output = '<table border=1 align=center>'
        output+='<tr><th><font size=3 color=white>Candidate Name</font></th>'
        output+='<th><font size=3 color=white>Party Name</font></th>'
        output+='<th><font size=3 color=white>Area Name</font></th>'
        output+='<th><font size=3 color=white>Image</font></th>'
        output+='<th><font size=3 color=white>Vote Count</font></th>'
        for i in range(len(partyList)):
            pl = partyList[i]
            count = getVoteCount(pl[0], pl[1])
            output+='<tr><td><font size=3 color=white>'+pl[0]+'</font></td>'
            output+='<td><font size=3 color=white>'+pl[1]+'</font></td>'
            output+='<td><font size=3 color=white>'+pl[2]+'</font></td>'
            output+='<td><img src="/static/parties/'+pl[3]+'" width=200 height=200></img></td>'
            output+='<td><font size=3 color=white>'+str(count)+'</font></td></tr>'
        output+="</table><br/><br/><br/><br/><br/><br/>"        
        context= {'data':output}
        return render(request, 'UserScreen.html', context)    

def AddElectionDate(request):
    if request.method == 'GET':
       return render(request, 'AddElectionDate.html', {})

def AddElectionDateAction(request):
    if request.method == 'POST':
        dd = request.POST.get('t1', False)
        with open("VotingApp/static/dd.txt", "wb") as file:
            dd = dd.encode()
            file.write(dd)
        file.close()
        context= {'data': "Election date & time details added"}
        return render(request, "AddElectionDate.html", context)

def AddVoterAction(request):
    if request.method == 'POST':
      global username, password, contact, email, address, usersList
      username = request.POST.get('t1', False)
      password = request.POST.get('t2', False)
      contact = request.POST.get('t3', False)
      email = request.POST.get('t4', False)
      address = request.POST.get('t5', False)
      aadhar = request.POST.get('aadhar', False)
      myfile = request.FILES['t6']
      status = "none"
      for i in range(len(usersList)):
          ul = usersList[i]
          if username == ul[0]:
              status = "exists"
              break
      if status == "none":
          status = 'User Details added to Blockchain with Finger image<br/><br/>'
          msg = contract.functions.createUser(username, email, password, contact, address, aadhar).transact()
          status += str(web3.eth.waitForTransactionReceipt(msg))
          usersList.append([username, password, email, aadhar])
          if os.path.exists('VotingApp/static/fingers/'+aadhar+'.tif'):
              os.remove('VotingApp/static/fingers/'+aadhar+'.tif')
          fs = FileSystemStorage()
          fs.save('VotingApp/static/fingers/'+aadhar+'.tif', myfile)    
      else:
          status = "Username already exists"
      context= {'data': status}
      return render(request, "AddVoter.html", context)

def AddVoter(request):
    if request.method == 'GET':
       return render(request, 'AddVoter.html', {})        

def AddCandidateAction(request):
    if request.method == 'POST':
        global partyList
        cname = request.POST.get('t1', False)
        pname = request.POST.get('t2', False)
        area = request.POST.get('t3', False)
        aadhar = request.POST.get('t5', False)
        myfile = request.FILES['t4']
        imagename = request.FILES['t4'].name
        status = "none"
        page = "AddCandidate.html"
        for i in range(len(partyList)):
            pl = partyList[i]
            if cname == pl[0] and pname == pl[1]:
                status = "Candidate & Party Name Already Exists"
                break
        if status == "none":
            if os.path.exists('VotingApp/static/parties/'+imagename):
                os.remove('VotingApp/static/parties/'+imagename)
            fs = FileSystemStorage()
            filename = fs.save('VotingApp/static/parties/'+imagename, myfile)
            status = 'Candidate details added to Blockchain<br/><br/>'
            msg = contract.functions.createParty(cname, pname, area, imagename, aadhar).transact()
            status += str(web3.eth.waitForTransactionReceipt(msg))
            partyList.append([cname, pname, area, imagename])
        context= {'data': status}
        return render(request, page, context)        

def UserLogin(request):
    if request.method == 'POST':
        global username, contract, usersList, latency
        username = request.POST.get('username', False)
        password = request.POST.get('password', False)
        myfile = request.FILES['t3']
        if os.path.exists('VotingApp/static/person.tif'):
            os.remove('VotingApp/static/person.tif')
        fs = FileSystemStorage()
        filename = fs.save('VotingApp/static/person.tif', myfile)
        start = timeit.default_timer()
        verification = FingerMatch.match('VotingApp/static/person.tif')
        status = "User.html"
        output = 'Invalid login or aadhar fingerprint verification failed'
        for i in range(len(usersList)):
            ulist = usersList[i]
            user1 = ulist[0]
            pass1 = ulist[1]
            if user1 == username and pass1 == password and ulist[3] == verification:
                status = "UserScreen.html"
                output = 'Welcome '+username+' your Fingerprint & Login Validation Successful from EVM Blockcahin.<br/>You can cast Vote'
                break
        end = timeit.default_timer()
        latency.append((end-start))
        context= {'data':output}
        return render(request, status, context)        

def AdminLogin(request):
    if request.method == 'POST':
        username = request.POST.get('username', False)
        password = request.POST.get('password', False)
        if username == 'admin' and password == 'admin':
            context= {'data':'Welcome Admin'}
            return render(request, "AdminScreen.html", context)
        else:
            context= {'data':'Invalid username'}
            return render(request, 'Admin.html', context)

def index(request):
    if request.method == 'GET':
       return render(request, 'index.html', {})

def Admin(request):
    if request.method == 'GET':
       return render(request, 'Admin.html', {})

def User(request):
    if request.method == 'GET':
       return render(request, 'User.html', {})    

def AddCandidate(request):
    if request.method == 'GET':
       return render(request, 'AddCandidate.html', {})



    
