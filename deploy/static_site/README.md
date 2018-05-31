# Building and Hosting a Static Site (on the cheap)

## Create an S3 bucket
We'll create an S3 bucket to store a pre-built static website.
S3 allows one to serve a publicly readable bucket as an HTTP website.

1. Create an S3 bucket with the domain name of our site (e.g., `example.com`).
2. Go to the bucket settings.
3. In the Permissions tab, set the Access Control List to allow everyone to "List Objects".
4. In the Permissions tab, add the following to the Bucket Policy, which will allow anyone to read objects:
    ```
    {
        "Version": "2012-10-17",
        "Id": "PublicBucketPolicy",
        "Statement": [
        {
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::example.com/*"
        }
        ]
    }
    ```
5. In the Properties tab, set the bucket to serve a static website
    1. Check "Use this bucket to host a website"
    2. The index document is `index.html`
    3. Change the error document to `404.html`


## Create a CloudFront Distribution
We can put CloudFront in front of the S3 bucket to serve as a CDN.
Additionally, this will allow us to use HTTPS (and redirect HTTP to HTTPS).

1. Create a distribution
    1. Set the origin domain name to `example.com.s3-website-us-west-2.amazonaws.com` (this will hopefully auto-fill)
    2. Change the "Viewer Protocol Policy" to "Redirect HTTP to HTTPS".
    3. Change the "Price Class" to "US, Canada, and Europe".
    4. Add alternate domain names:
        ```
        custemcamp.org
        www.custemcamp.org
        ```
    5. Request a Certificate with ACM.  It should cover `example.com` and `www.example.com`.
       If you got your domain through Route 53, you can validate it with DNS validation, which will simply require you to add a new record set in your hosted zone.

2. Get some coffee and wait fot the CloudFront distribution to get started.
3. Get `example.com` pointed to the CloudFront DNS by creating some Route53 record sets:
    1. Click "Create Record Set" to point `example.com` to the CloudeFront domain.
        * Leave "Name" blank, since we're going to set up the base domain.
        * Leave "Type" as "A - IPv4 address"
        * Leave time to live (TTL) as 300 seconds
        * For "Value", enter the domain name of the CloudFront distribution.
        * "Routing Policy" can be "Simple".
        * Click "Create"
    2. Repeat 1. for "Type" as "AAAA - IPv6 address".
    3. Repeat 1. and 2. for `www.example.com`.


## Build the Jekyll Website
I build the website on my local box, and then copy the site over to S3.

1. Ensure you have `bundler` installed (provided by the `bundler` package in Ubuntu)
2. Run `./bundle_install.sh`
3. Run `./build.sh` to build the site (or `./serve_local_dev.sh` if you want to work interactively).


## Update S3 and CloudFront
Now that we have the S3 bucket and CloudFront CDN set up, and the static site built on our local box, let's push it to the bucket and force the CDN to update itself.

1. Ensure you have the AWS CLI installed and configured for your IAM user.
   The package is called called `awscli` on Ubuntu.
   Information on configuring the AWS CLI can be found here: https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html.

   You should create a profile with the same name as your IAM user.
   ```bash
   aws configure --profile $IAM_USER
   ```

2. Make a file named `aws_env` with the following
    ```bash
    IAM_USER=username
    IAM_ID=NNNNNNNNNNNN

    CLOUDFRONT_DISTRIBUTION_ID=XXXXXXXXXXXXXXXXXX

    S3_BUCKET_NAME=example.com
    S3_ENDPOINT_NAME=http://example.com.s3-website-us-west-2.amazonaws.com
    ```

3. Get a temporary IAM session with
    ```bash
    source get_temp_session NNNNN
    ```
    where NNNNNN is the MFA code from your MFA device.

4. Push the updated site to the S3 bucket with `./update_s3.sh`.
5. Create a cache invalidation to get all the CloudFront nodes updated `./create_invalidation.sh`.
