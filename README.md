# school_automations
school automations for Parent Committee and more

the overall ambition is to have a tool, that minimizes human involvement in the collecting, payment, and monitoring the comettes funds.
what I cannot do yet?
- all paybox interactions.

what I dont want to do:
- send group whatsapp massages (easy manually)

project status:

1- calculate amount to collect based on a specifically defined input.-----------------done

2- manage collection (ask from however did not pay)

3- monitoring.

how to manage collecting and monitor?

manage collecting:
- parse the paybox traffic and parents phone numbers to see how payed
- periodically send whatsapp messages to remind however did not pay and send myself a report

monitor:
- parse paybox traffic to see what was payed
- save screenshots (best from whatsapp to the teacher)
- write to the monitor tab
- send a monthly report
- 





a side project( linked to section 1):
- from mail, generate an .ics file with leaves. ------------------------------------------done 



actual redme:

recuirements: ....
create a google sheet in this format (input tab): https://docs.google.com/spreadsheets/d/1dx4lOYBhhNl57gLA9uLuINQ3fhBYElpGS0MwOPwzjEA/edit?gid=62455841#gid=62455841

give a path to your credentials file (to manage read/write to  google sheet)
instructions on how to generate a credentials file can be found here:https://developers.google.com/workspace/guides/create-credentials?hl=he

note that the input is rigid- do not change its format.