"""
    This program sends a message to a queue on the RabbitMQ server.
    Make tasks harder/longer-running by adding dots at the end of the message.

    Author: Denise Case
    Date: January 15, 2023

    Modifiedy by: Jarrod Sims
    Date: September 17, 2023
"""

import pika
import sys
import webbrowser
import logging
import time
import csv

# Configure RabbitMQ
rabbit_host = 'localhost'
queue_name = 'task_queue2'
SHOW_OFFER = True #If true, RabbitMQ admin site will open automatically

#Insert CSV file
csv_file = 'tasks.csv'

def offer_rabbitmq_admin_site():
    """Offer to open the RabbitMQ Admin website"""
    global SHOW_OFFER
    if SHOW_OFFER:
        webbrowser.open_new("http://localhost:15672/#/queues")
        print()

def send_message(host: str, queue_name: str, message: str):
    """
    Creates and sends a message to the queue each execution.
    This process runs and finishes.

    Parameters:
        host (str): the host name or IP address of the RabbitMQ server
        queue_name (str): the name of the queue
        message (str): the message to be sent to the queue
    """

    try:
        # create a blocking connection to the RabbitMQ server
        conn = pika.BlockingConnection(pika.ConnectionParameters(host))
        # use the connection to create a communication channel
        ch = conn.channel()
        # use the channel to declare a durable queue
        # a durable queue will survive a RabbitMQ server restart
        # and help ensure messages are processed in order
        # messages will not be deleted until the consumer acknowledges
        ch.queue_declare(queue=queue_name, durable=True)
        # use the channel to publish a message to the queue
        # every message passes through an exchange
        ch.basic_publish(exchange="", routing_key=queue_name, body=message)
        # print a message to the console for the user
        #print(f" [x] Sent {message}")
        
        #log message
        dot_count = message.count('.')
        time.sleep(dot_count)
        logging.info(f" [x] Sent {message}")
    
    except pika.exceptions.AMQPConnectionError as e:
        print(f"Error: Connection to RabbitMQ server failed: {e}")
        sys.exit(1)
    finally:
        # close the connection to the server
        conn.close()


def main(csv_file_path: str):
    # Open RabbitMQ Admin site
    offer_rabbitmq_admin_site()

    # Read tasks from CSV file
    with open(csv_file, 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader) # skip the header row
        try:
           for row in reader:
               message = ','.join(row)  # Convert row to a comma-separated string
               message = message+".."
               send_message(rabbit_host, queue_name, message)
        except KeyboardInterrupt:
                print()
                print(" [x] Exiting application with CTRL+C")
                sys.exit(0)

# Standard Python idiom to indicate main program entry point
# This allows us to import this module and use its functions
# without executing the code below.
# If this is the program being run, then execute the code below
if __name__ == "__main__":  
    # Specify the CSV file name as a command-line argument
    print(" [*] Ready for work. To exit press CTRL+C")
    try:
        if len(sys.argv) != 2:
            print("Usage: python3 v3_emitter_of_tasks.py <csv_file>")
            sys.exit(1)

        csv_file = sys.argv[1]
        main(csv_file)
    except KeyboardInterrupt:
        print()
        print(" User interrupted process with CTRL-C keyboard shortcut.")
        sys.exit(0)