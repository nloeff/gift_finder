# GPTsy
## An app to find the perfect gift at Etsy using GPT-3

![GPTsy is awesome!](/app/assets/images/gptsy.png)

 ### Instructions to run

 1. Install requirements.txt to your virtualenv of choice
 2. run
 ```
 python3 app/GPTsy.py --api-key=<INSERT YOUR OWN OPENAI API KEY>
 ```
 3. Open http://127.0.0.1:8888 in your browser 


### Caveats
Too many to list. Top 4:
* Code is slow/unoptimized, and each run takes about 20 seconds
* Queries are not sanitized in any way --- it is easy to break this by appending 'ignore the previous prompt' to the query or other malicious prompt.
* GPT-3 results are not guaranteed to have the right format, or be coherent, or not be offensive or biased.
* Code does not currently handle errors.

This is a prototype, not a production system, USE AT YOUR OWN RISK.

### Acknowledgements
Flask App based on @andrew's xwalk-browser