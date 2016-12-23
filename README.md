LunchTrain V2
======================

A Slack integration intended to help its users collaborate on places to get lunch

You can find an article I've written on ideology behind LunchTrain here -> http://clypd.com/staying-on-track-for-lunchtime/

Usage (from within Slack, presumes set up with /train as the slash cmd):

<code> /train help </code> Displays the help 

<code> /train start <Destination> <Duration (int, minutes)> </code> Starts a train to <Destination> that leaves in <Duration> mins

<code> /train join <Destination> </code> Joins a train going to the specified destination

<code> /train active </code> Reports a list of all the active trains and the time left on them

Changelog from the HipChat version:
- No more /train passengers (felt it was deprecated)

Deployment setup notes:
I'm still working on a proper deployment where it pulls the appropriate Slack webhook URL from an Environment URL, but for now this'll probably be fine

1) Go to https://<slack-name>.slack.com/apps/build/custom-integration

2) Click "Add Slash Command"

3) Set the command to '/train' (for continuity's sake, and that's how I set everything up anyway)

4) Configure options as follows: URL: 'https://lunchtrainv2.herokuapp.com', Method: POST, Name: 'LunchTrain', Emoji: 🚂 (I liked this one best)

5) Go back to https://<clypd-slack-name>.slack.com/apps/build/custom-integration

6) Click "Add Incoming Webhook"

7) Configure options to: Post to "Notwork" (or wherever), set Name and Emoji to the same as in Step 4. Copy the 'Webhook URL' somewhere

8) Clone a copy of this repo, and replace the 'webhook_url' variable with the URL from the previous step (found at Train.py, line 211)

9) Add/Commit changes, push to master, will take a few mins to auto-rebuild 

10) Fingers crossed everything works, please let me know if the app crashes or you encounter any unexpected behavior. 
I rewrote everything in an effort to learn Python & it's the first real multithreaded program I've written that's not in Go. 
