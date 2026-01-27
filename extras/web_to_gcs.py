import os
import requests
from google.cloud import storage
from dotenv import load_dotenv
from tqdm import tqdm


"""
Pre-reqs: 
1. `pip install pandas pyarrow google-cloud-storage python-dotenv`
2. Set GOOGLE_APPLICATION_CREDENTIALS to your project/service-account key
3. Set GCP_GCS_BUCKET as your bucket or change default value of BUCKET
"""
load_dotenv()

# services = ['fhv','green','yellow']
init_url = "https://d37ci6vzurychx.cloudfront.net/trip-data/"
# switch out the bucketname
BUCKET = os.environ.get("GCP_GCS_BUCKET", "dtc-data-lake-bucketname")


def download_with_progress(url: str, local_path: str, desc: str = "Downloading"):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        total = int(r.headers.get("content-length", 0))
        # Configure tqdm for bytes
        with (
            open(local_path, "wb") as f,
            tqdm(
                total=total,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
                desc=desc,
            ) as bar,
        ):
            for chunk in r.iter_content(chunk_size=1024 * 1024):  # 1 MB
                if not chunk:
                    continue
                size = f.write(chunk)
                bar.update(size)


def upload_to_gcs_with_progress(bucket: str, object_name: str, local_file: str):
    # # WORKAROUND to prevent timeout for files > 6 MB on 800 kbps upload speed.
    # # (Ref: https://github.com/googleapis/python-storage/issues/74)
    # Optional: tune chunk size (must be multiple of 256 KiB)
    storage.blob._MAX_MULTIPART_SIZE = 5 * 1024 * 1024  # 5 MB
    storage.blob._DEFAULT_CHUNKSIZE = 5 * 1024 * 1024   # 5 MB

    client = storage.Client()
    bucket_obj = client.bucket(bucket)
    blob = bucket_obj.blob(object_name)

    if blob.exists(client):
        print(f"Skipping upload, already in GCS: gs://{bucket}/{object_name}")
        return

    file_size = os.path.getsize(local_file)

    with open(local_file, "rb") as f:
        with tqdm.wrapattr(
            f,
            "read",
            total=file_size,
            miniters=1,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            desc=f"Uploading {os.path.basename(local_file)}",
        ) as wrapped_file:
            blob.upload_from_file(
                wrapped_file,
                size=file_size,  # important so the library knows total bytes
            )

    print(f"Uploaded to GCS: gs://{bucket}/{object_name}")


def web_to_gcs(year, service):
    client = storage.Client()
    bucket_obj = client.bucket(BUCKET)

    for i in tqdm(range(6), desc=f"{service} {year}", unit="month"):
        month = f"{i + 1:02d}"

        parquet_file_name = f"{service}_tripdata_{year}-{month}.parquet"
        object_name = f"{service}/{parquet_file_name}"

        # 1) Check if parquet already in GCS
        blob = bucket_obj.blob(object_name)
        if blob.exists(client):
            print(f"Already in GCS, skipping: gs://{BUCKET}/{object_name}")
            continue

        # 2) Check if parquet already downloaded locally
        if os.path.exists(parquet_file_name):
            print(f"parquet already exists locally, skipping download: {parquet_file_name}")
        else:
            request_url = f"{init_url}{parquet_file_name}"
            download_with_progress(
                request_url, parquet_file_name, desc=f"Downloading {parquet_file_name}"
            )

        # 4) Upload with per-byte progress bar
        upload_to_gcs_with_progress(BUCKET, object_name, parquet_file_name)



web_to_gcs("2024", "yellow")
