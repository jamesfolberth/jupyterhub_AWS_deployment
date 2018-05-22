# Setting up Webserver Stuff
We want to serve static webpages from `example.com` and the hub from `hub.example.com`.
The configuration files in this directory set this up.
We expect to have ports 22, 80, and 443 open.
If the user goes to either site over HTTP, we redirect them to port 443 to use HTTPS.

We do all this in a few pieces.
We first create SSL/TLS certificates with [Let's Encrypt](https://letsencrypt.org/).
We then register a domain name and set up routing, including to the subdomain.
Finally, we install and configure `nginx`.


TODO JMF 22 May 2018: mention that user should change `example.com` in conf files


## SSL/TLS certificate with Let's Encrypt
This is assuming we're generating certs for `example.com`.
This will obviously be different for your site.
We're going to use `example.com` to serve static HTML pages, and `hub.example.com` for Jupyterhub, so we'll actually do this twice.
The certs we generate are output to `/etc/letsencrypt/live/`

1. Generate an SSL/TLS key with [Let's Encrypt](https://letsencrypt.org/).
   ```bash
   cd && cd repos
   git clone https://github.com/letsencrypt/letsencrypt
   cd letsencrypt
   sudo ./letsencrypt-auto certonly --standalone -v -d hub.example.com --debug # need debug on Amazon Linux
   ```

2. Generate D-H parameters
   ```bash
   sudo openssl dhparam -out /etc/letsencrypt/live/hub.example.com/dhparams.pem 2048
   ```


## Set up domain name and routing
1. We used Amazon [Route 53](https://aws.amazon.com/route53/) to register the domain name `example.com`.
   We also create a new [Elastic IP](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/elastic-ip-addresses-eip.html) and associate it with the EC2 instance running the hub and `nginx`.
   For now, the Jupyterhub instance will run the hub as well as serve static HTML, so we set up hosted zones to point to the elastic IP we allocated for the hub instance.
   We can change that later, though.

   To point our domain (and subdomain) to the right IP, we need to set up a couple hosted zones.
   We follow the instructions [here](https://aws.amazon.com/premiumsupport/knowledge-center/create-subdomain-route-53/) to set up the subdomain.

3. Set the hosted zone to route to `example.com`.
   1. Sign in to the [Route 53](https://console.aws.amazon.com/route53/home) console and click the "Hosted zones" from the navigation pane on the left.
      This assumes you already have a hosted zone that was created when you registered your domain with Route 53.
   2. Enter the following information into the corresponding fields and create the hosted zone:
      * For Domain Name, type your domain name (`example.com`).
      * For Comment, type text that describes what the subdomain does or is for.
      * For Type, choose Public.
   3. Click "Create Record Set" to point the domain to the elastic IP allocatd earlier.
      * Leave "Name" blank, since we're going to set up the base domain.
      * Leave "Type" as "A - IPv4 address"
      * Leave time to live (TTL) as 300 seconds
      * For "Value", enter the elastic IP allocated earlier and associated with the hub/`nginx` instance.
      * "Routing Policy" can be "Simple".
      * Click "Create"

4. Repeat step 3. for `hub.example.com`, using the same hosted zone.


## Setting up nginx
1. On the AMI we've used (one of the Amazon Linux flavors), `nginx` is in the repos, so install it with

   ```bash
   sudo yum install nginx
   sudo service nginx start
   ```

   You can test the nginx install by pointing your web browswer to the IP of the EC2 instance.
   You should see a default `index.html`.

   Nginx has a [basic setup guide](https://www.nginx.com/blog/setting-up-nginx/).

2. Now copy over the configuration files from this directory.
   These files are pretty much exactly the configuration files from [Jupyterhub's examples](http://jupyterhub.readthedocs.io/en/latest/config-examples.html).
   At the time of writing, they haven't written the AWS+NGINX
   We use a HTTP->HTTPS redirection from [Bjorn Johansen](https://www.bjornjohansen.no/redirect-to-https-with-nginx).

   Rename the default config.
   ```bash
   sudo su
   cd /etc/nginx/
   mv nginx.conf nginx.conf.bak
   ```
   Now copy (still as root) over `nginx.conf` to `/etc/nginx/nginx.conf`, and `conf.d` to `/etc/nginx/confg.d`.
   Edit these files to point to your SSL/TLS certs and D-H parameters.

3. The static HTML server expects files in `/data/www`.
   The proxy to the hub expects to the hub to be serving on port 8000 of the localhost.

4. Reload nginx files with `sudo nginx -s reload`.
