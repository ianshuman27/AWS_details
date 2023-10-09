from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.models import User
import boto3
import csv
from django.core.mail import EmailMessage
from .email_utils import send_email_with_attachment
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.http import (HttpResponseBadRequest,
                         HttpResponse,
                         HttpResponseForbidden,
                         HttpResponseNotFound,
                         HttpResponseNotAllowed,
                         HttpResponseServerError,
                         Http404,
                         BadHeaderError,
                         HttpRequest)



@csrf_exempt
def user_info(request):
    if request.method=='POST':
        json_data = json.loads(request.body)
        username=json_data["username"]
        password=make_password(json_data["password"])
        user=User.objects.create(username=username, password=password)
        return HttpResponse("username has been stored in db",status=200)

    else:
        return HttpResponse("only POST request is allowed",status=400)
   


def aws_info(request):
    ec2_cli= boto3.client(
                'ec2',
                region_name="us-east-1",
                aws_access_key_id= "AKIA4IKQPTEIIMYNM6WR",
                aws_secret_access_key="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"
            )
    collect_all_regions=[]
    for each_region in ec2_cli.describe_regions()['Regions']: 
             collect_all_regions.append(each_region['RegionName'])
    print(collect_all_regions)

    fo=open('ec2_inven_new1.csv','w',newline='')
    data_obj=csv.writer(fo)
    data_obj.writerow(['Sno','InstanceID',"InstanceType",'KeyName',"Private_ip","Public_IP"])
    cnt=1
    for each_region in collect_all_regions:
        ec2_re=boto3.resource('ec2',
                region_name=each_region,
                aws_access_key_id= "AKIA4IKQPTEIIMYNM6WR",
                aws_secret_access_key="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")
        for each_ins_in_reg in ec2_re.instances.all():
            data_obj.writerow([cnt,each_ins_in_reg.instance_id,each_ins_in_reg.instance_type,each_ins_in_reg.key_name,each_ins_in_reg.private_ip_address,each_ins_in_reg.public_ip_address])
            cnt+=1
    fo.close()
    return HttpResponse("AWS details has been stored successfully",status=200)



def my_email_with_attachment_view(request):
    subject = 'Email from Django'
    message = 'Hi Anshuman, Please find the attached file containg AWS ec2 instance details.'
    recipient_list = ['anshumanyadav7388@gmail.com']  
    file_path = f"{settings.BASE_DIR}/ec2_inven_new1.csv"

    send_email_with_attachment(subject, message, recipient_list,file_path)

    return HttpResponse("Email with Attachment Sent Successfully!",status=200)
   

    
  
