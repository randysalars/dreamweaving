# Video storage

Source: https://notion.so/20b2bab3796d80eb8a41ec0e11a9e1cd
Last edited: 2025-06-07T23:24:00.000Z
Page ID: 20b2bab3-796d-80eb-8a41-ec0e11a9e1cd

---

<details><summary>Great call! Wasabi is a solid choice—cheap, reliable, and perfect for hosting your Dreamweaver videos to embed or link from your Next.js site. Here’s a step-by-step guide to get you going:</summary>
  ## 1. Sign Up for Wasabi

  - Go to wasabi.com and create a free trial account (no credit card needed for the trial).
  ---

  ## 2. Create a Storage Bucket

  - Once logged in, go to the Buckets section.
  - Click Create Bucket.
  - Pick a region close to your main audience (US West, US East, etc.).
  - Give it a unique name (like dreamweaver-videos-randy).
  ---

  ## 3. Upload Your Videos

  - Enter your bucket.
  - Use the drag-and-drop interface OR the “Upload Files” button to upload your video files (.mp4 works best for web).
  ---

  ## 4. Make Files Public

  - By default, files are private.
  - To let your site visitors watch your video:
    1. Click the file (video) in your bucket.
    1. In the file details, find Permissions or Access Control List (ACL).
    1. Add a rule to allow Everyone/All Users to Read (view) the object.
  ---

  ## 5. Grab the Video URL

  - Select the video you just uploaded.
  - Copy the Object URL—it’ll look like this:https://s3.us-west-1.wasabisys.com/dreamweaver-videos-randy/your-video.mp4
  ---

  ## 6. Embed in Your Next.js Site

  Use a simple HTML5 player in your React code:

  ```javascript
  <video controls width="720">
  <source src="<https://s3.us-west-1.wasabisys.com/dreamweaver-videos-randy/your-video.mp4>" type="video/mp4" />
  Sorry, your browser does not support the video tag.
</video>

  ```

  ---

  ## Extra Tips

  - Test your links before you go live!
  - Keep videos under 2–3GB each for best web compatibility.
  - You can organize lots of videos into folders inside your bucket.
  - Need privacy? Wasabi has options for signed URLs or private links, but just sharing a public link is simplest.
  ---

  Want a detailed walk-through with screenshots? Or help linking Wasabi into your Next.js site with a fancier video player or custom features? Let me know what you’d like next!


<details><summary>cloudflare cdn</summary>
  I'll help you set up Cloudflare CDN in front of your Wasabi storage to get better video delivery performance. Here's how to do it step by step:

  ### 1. Initial Setup Requirements:

  - Your existing Wasabi bucket with videos
  - A domain name you control
  - A Cloudflare account (free tier is fine to start)
  Let me search for the most current setup instructions and best practices.Here’s what I found about setting up Cloudflare CDN with Wasabi:

  ### Step-by-Step Guide

  ### Step 1: Create Your Wasabi Bucket

  - Go to Wasabi and create a bucket if you haven’t already.
  - The bucket name should ideally match the subdomain or domain you want to use. For example, if you want your videos to be accessible at videos.mydomain.com, name your bucket videos.
  ---

  ### Step 2: Enable Public Access on Your Wasabi Bucket

  - Make sure any videos you upload are accessible publicly.
  1. Go to your bucket settings in Wasabi.
  1. Enable public access.
  1. Update permissions to allow files to be read by "Everyone."
  Wasabi supports S3-compatible object URLs like:

  https://s3.<region>.wasabisys.com/<bucketname>/file.mp4

  ---

  ### Step 3: Add Custom Domain in Cloudflare

  Go to Cloudflare

  - Sign in and select the domain you want to use.
  Set Up DNS

  1. Go to the DNS Dashboard in Cloudflare for your domain.
  1. Add a CNAME record:
    - Name (Subdomain): e.g., videos (if using videos.mydomain.com).
    - Target: Your Wasabi bucket endpoint (e.g., s3.us-west-1.wasabisys.com).
    - TTL: Leave it at "Auto."
    - Proxy status: Set to Proxied (orange cloud). This ensures traffic goes through Cloudflare's CDN.
  ---

  ### Step 4: Configure SSL (Optional but Recommended)

  - Go to SSL/TLS Settings in Cloudflare.
  - Choose Flexible or Full to enable HTTPS for your video links.
  - This can eliminate any browser warnings about insecure content.
  ---

  ### Step 5: Test Your Setup

  - Visit https://videos.mydomain.com/your-video.mp4 to verify that the video is accessible over Cloudflare.
  ---

  ### Step 6: Embed Videos on Your Site

  Once your videos are working properly, update your Next.js project to embed them, like so:

  ```javascript
  <video controls width="720">
  <source src="<https://videos.mydomain.com/your-video.mp4>" type="video/mp4" />
  Your browser does not support the video tag.
</video>

  ```

  ---

  ### Pros of Using Cloudflare + Wasabi

  - Improved Speed: Cloudflare serves your videos from the closest edge server to your users for faster load times.
  - Savings on Egress Costs: Cloudflare caches video, reducing bandwidth costs on Wasabi.
  - HTTPS Security: Integrates SSL for your custom domain.
  - Global Reach: Better performance for international users.
  ---

  Would you like a detailed guide for setting CNAME or securing your Wasabi links further? Let me know!


---
