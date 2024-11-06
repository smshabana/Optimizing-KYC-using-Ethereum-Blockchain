import os
from flask import Flask, render_template, request 
import json
from web3 import Web3, HTTPProvider
from datetime import datetime[p[-7]]
import pickle

app = Flask(__name__)

global details
details = ''
global user_id

def readDetails(contract_type):
    global details
    details = ""
    print(contract_type+"======================")
    blockchain_address = 'http://127.0.0.1:8545' #Blokchain connection IP
    web3 = Web3(HTTPProvider(blockchain_address))
    web3.eth.defaultAccount = web3.eth.accounts[0]
    compiled_contract_path = 'KYC.json'
    deployed_contract_address = '0x5830eD9AF84087500F6702e3E1D375dDD4AdDa7E' #hash address to access bank contract
    with open(compiled_contract_path) as file:
        contract_json = json.load(file)  # load contract info as JSON
        contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions
    file.close()
    contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi) #now calling contract to access data
    if contract_type == 'adduser':
        details = contract.functions.getUsers().call()
    if contract_type == 'account':
        details = contract.functions.getBankAccount().call()
    if contract_type == 'status':
        details = contract.functions.getstatus().call()
    if len(details) > 0:
        if 'empty' in details:
            details = details[5:len(details)]    
    print(details)    

def saveDataBlockChain(currentData, contract_type):
    global details
    global contract
    details = ""
    blockchain_address = 'http://127.0.0.1:8545'
    web3 = Web3(HTTPProvider(blockchain_address))
    web3.eth.defaultAccount = web3.eth.accounts[0]
    compiled_contract_path = 'KYC.json' 
    deployed_contract_address = '0x5830eD9AF84087500F6702e3E1D375dDD4AdDa7E' #bank contract address
    with open(compiled_contract_path) as file:
        contract_json = json.load(file)  # load contract info as JSON
        contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions
    file.close()
    contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
    readDetails(contract_type)
    if contract_type == 'adduser':
        details+=currentData
        msg = contract.functions.addUsers(details).transact()
        tx_receipt = web3.eth.waitForTransactionReceipt(msg)
    if contract_type == 'account':
        details+=currentData
        msg = contract.functions.bankAccount(details).transact()
        tx_receipt = web3.eth.waitForTransactionReceipt(msg)
    if contract_type == 'status':
        details+=currentData
        msg = contract.functions.addstatus(details).transact()
        tx_receipt = web3.eth.waitForTransactionReceipt(msg)
    



@app.route('/SendAmountAction', methods=['POST'])
def SendAmountAction():
    global details
    if request.method == 'POST':
        sender = request.form['t1']
        balance = request.form['t2']
        receiver = request.form['t3']
        amount = request.form['t4']
        amount = float(amount)
        balance = float(balance)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if balance > amount:
            data = sender+"#"+str(amount)+"#"+str(timestamp)+"#Sent To "+receiver+"\n"
            saveDataBlockChain(data,"account")
            data = receiver+"#"+str(amount)+"#"+str(timestamp)+"#Received From "+sender+"\n"
            saveDataBlockChain(data,"account")
            context= 'Money sent to '+receiver
            return render_template('UserScreen.html', msg=context)
        else:
            context= 'Insufficient balance'
            return render_template('UserScreen.html', msg=context)


@app.route('/SendAmount', methods=['GET','POST'])
def SendAmount():
    if request.method == 'GET':
        global user_id
        readDetails("account")
        deposit = 0
        wd = 0
        rows = details.split("\n")
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if arr[0] == user_id:
                if arr[3] == 'Self Deposit' or "Received From " in arr[3]:
                    deposit = deposit + float(arr[1])
                else:
                    wd = wd + float(arr[1])
        deposit = deposit - wd            
        output = '<tr><td><font size="3" color="black">Username</td><td><input type="text" name="t1" size="20" value='+user_id+' readonly/></td></tr>'
        output += '<tr><td><font size="3" color="black">Available&nbsp;Balance</td><td><input type="text" name="t2" size="20" value='+str(deposit)+' readonly/></td></tr>'
        output += '<tr><td><font size="3" color="black">Choose&nbsp;Receiver&nbsp;Name</td><td><select name="t3">'
        readDetails("status")
        rows = details.split("\n")
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if arr[0] == "accepted":
                if arr[1] != user_id:
                    output += '<option value="'+arr[1]+'">'+arr[1]+'</option>'
        output += "</select></td></tr>"
            
        return render_template('SendAmount.html', msg1=output)

@app.route('/ViewBalance', methods=['GET','POST'])
def ViewBalance():
    if request.method == 'GET':
        global user_id
        output = '<table border=1 align=center width=100%>'
        font = '<font size="3" color="black">'
        arr = ['Username','Amount','Transaction Date',"Transaction Status"]
        output += "<tr>"
        for i in range(len(arr)):
            output += "<th>"+font+arr[i]+"</th>"
        readDetails("account")
        rows = details.split("\n")
        deposit = 0
        wd = 0
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if arr[0] == user_id:
                output += "<tr><td>"+font+arr[0]+"</td>"
                output += "<td>"+font+arr[1]+"</td>"
                output += "<td>"+font+arr[2]+"</td>"
                output += "<td>"+font+arr[3]+"</td>"
                if arr[3] == 'Self Deposit' or "Received From " in arr[3]:
                    deposit = deposit + float(arr[1])
                else:
                    wd = wd + float(arr[1])
        deposit = deposit - wd
        output += "<tr><td>"+font+"Current Balance : "+str(deposit)+"</td>"
               
        return render_template('ViewBalance.html', msg=output)  

@app.route('/LoginAction', methods=['POST'])
def LoginAction():
    global details
    global user_id
    if request.method == 'POST':
        username = request.form['t1']
        password = request.form['t2']
        status = 'none'
        readDetails("status")
        rows = details.split("\n")
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if arr[0] == "accepted":
                if arr[1] == username and arr[2] == password:
                    status = 'success'
                    user_id = username
                    break
        if status == 'success':
            file = open('session.txt','w')
            file.write(username)
            file.close()
            context= "Welcome "+username
            return render_template('UserScreen.html', msg=context)
        else:
            context= 'Invalid login details'
            return render_template('Login.html', msg=context) 

@app.route('/BankerLoginAction', methods=['POST'])
def BankerLoginAction():
    if request.method == 'POST':
        username = request.form['t1']
        password = request.form['t2']
        if username == 'admin' and password == 'admin':
            context = "Welcome Banker"
            return render_template('BankerScreen.html', data=context)
        else:
            context = "Invalid Details"
            return render_template('BrankerLogin.html', data=context)

@app.route('/DepositAction', methods=['POST'])
def DepositAction():
    global details
    if request.method == 'POST':
        username = request.form['t1']
        amount = request.form['t2']
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data = username+"#"+amount+"#"+str(timestamp)+"#Self Deposit\n"
        saveDataBlockChain(data,"account")
        context= 'Money added to user account '+username
        return render_template('Deposit.html', msg=context)


@app.route('/SignupAction', methods=['POST'])
def SignupAction():
    global details
    if request.method == 'POST':
        username = request.form['t1']
        password = request.form['t2']
        fname = request.form['t3']
        lname = request.form['t4']
        occ = request.form['t5']
        inrange = request.form['t6']
        dob = request.form['t7']
        gen = request.form['t8']
        fadd = request.form['t9']
        pn1 = request.form['t10']
        pn2 = request.form['t11']
        email = request.form['t12']
        country = request.form['t13']
        
        record = 'none'
        readDetails("adduser")
        rows = details.split("\n")
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if arr[0] == "adduser":
                if arr[1] == username:
                    record = "exists"
                    break
        if record == 'none':
            data = "adduser#"+username+"#"+password+"#"+fname+"#"+lname+"#"+occ+"#"+inrange+"#"+dob+"#"+gen+"#"+fadd+"#"+pn1+"#"+pn2+"#"+email+"#"+country+"\n"
            saveDataBlockChain(data,"adduser")
            context='Request sent to the banker.'
            return render_template('Signup.html', msg=context)
        else:
            context=username+' Username already exists'
            return render_template('Signup.html', msg=context)  

@app.route('/Deposit', methods=['GET','POST'])
def Deposit():
    if request.method == 'GET':
        global user_id
        output = '<tr><td><font size="3" color="black">Username</td><td><input type="text" name="t1" size="20" value='+user_id+' readonly/></td></tr>'
        return render_template('Deposit.html', msg1=output) 


def check_status(name):
    readDetails('status')
    arr = details.split("\n")
    for i in range(len(arr)-1):
        array = arr[i].split("#")
        if array[1] == name:
            return True
            break
    return False

@app.route('/CheckUser', methods=['GET', 'POST'])
def CheckUser():
    if request.method == 'GET':
        global username,password
        output = '<table border="1" align="center" width="100%">'
        font = '<font size="3" color="black">'
        headers = ['Username', 'Password','First Name', 'Middle Name' ,'Occupation','Income Range','DOB','Gender','Full Residential Address','Phone Number 1','Phone Number 2','Email','Country of Residence','Action']

        output += '<tr>'
        for header in headers:
            output += f'<th>{font}{header}{font}</th>'
        output += '</tr>'

        readDetails('adduser')
        arr = details.split("\n")

        for i in range(len(arr) - 1):
            array = arr[i].split("#")

            output += '<tr>'
            for cell in array[1:14]:
                output += f'<td>{font}{cell}{font}</td>'
            action_cell = f'<td><a href="/SubmitStatus?username={array[1]}&password={array[2]}">{font}Click Here to Accept/Decline{font}</a></td>' if not check_status(array[1]) else f'<td>{font}Already Submitted{font}</td>'

            output += action_cell
            output += '</tr>'

        output += '</table><br/><br/><br/>'

        return render_template('CheckUser.html', data=output)

@app.route('/SubmitStatus', methods=['GET', 'POST'])
def SubmitStatus():
    global username,password

    if request.method == 'GET':
        username = request.args.get('username')
        password = request.args.get('password')
        return render_template('SubmitStatus.html')

    if request.method == 'POST':
        status = request.form['t1']
        data = status+"#"+username+"#"+password+"\n"
        saveDataBlockChain(data, "status")

        context = "Status Marked Successfully."

        return render_template('SubmitStatus.html', data=context)


@app.route('/Deposit', methods=['GET', 'POST'])
def Deposits():
    if request.method == 'GET':
       return render_template('Deposit.html', msg='')

@app.route('/Login', methods=['GET', 'POST'])
def Login():
    if request.method == 'GET':
       return render_template('Login.html', msg='')

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
       return render_template('index.html', msg='')

@app.route('/SendAmount', methods=['GET', 'POST'])
def SendAmounts():
    if request.method == 'GET':
       return render_template('SendAmount.html', msg='')

@app.route('/Signup', methods=['GET', 'POST'])
def Signup():
    if request.method == 'GET':
       return render_template('Signup.html', msg='')

@app.route('/UserScreen', methods=['GET', 'POST'])
def UserScreen():
    if request.method == 'GET':
       return render_template('UserScreen.html', msg='')

@app.route('/ViewBalance', methods=['GET', 'POST'])
def ViewBalances():
    if request.method == 'GET':
       return render_template('ViewBalance.html', msg='')


@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
       return render_template('index.html', msg='')

@app.route('/SubmitStatus', methods=['GET', 'POST'])
def SubmitStatuss():
    if request.method == 'GET':
       return render_template('SubmitStatus.html', msg='')

@app.route('/BankerLogin', methods=['GET', 'POST'])
def BankerLogins():
    if request.method == 'GET':
       return render_template('BankerLogin.html', msg='')

@app.route('/BankerScreen', methods=['GET', 'POST'])
def BankerScreens():
    if request.method == 'GET':
       return render_template('BankerScreen.html', msg='')


if __name__ == '__main__':
    app.run()  