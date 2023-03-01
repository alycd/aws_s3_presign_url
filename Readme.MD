## Generate AWS S3 POST URL to Upload File

1. Checks if key already exists : TODO -> take epoch filename as timestamp and generate YYYY/MM/DD key
2. TODO : check content-length against supplied file to see if data is incomplete or partial upload
3. Generate presigned URL dictionary -> to be passed to client application
4. Generate cURL command to test locally

`data = bucket_wrapper.generate_presigned_post('1677634244.gz', 3600)`

Change the '1677634244.gz' filename after you have uploaded sucessfully, otherwise it will say the file exists.

