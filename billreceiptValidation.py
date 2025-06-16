# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# [START documentai_process_document]
from typing import Optional

from google.api_core.client_options import ClientOptions
from google.cloud import documentai  # type: ignore
import magic
from imageCountValidation import count_faces, detect_faces
from google.protobuf.json_format import MessageToDict

# TODO(developer): Uncomment these variables before running the sample.
# project_id = "YOUR_PROJECT_ID"
# location = "YOUR_PROCESSOR_LOCATION" # Format is "us" or "eu"
# processor_id = "YOUR_PROCESSOR_ID" # Create processor before running sample
# file_path = "/path/to/local/pdf"
# mime_type = "application/pdf" # Refer to https://cloud.google.com/document-ai/docs/file-types for supported file types
# field_mask = "text,entities,pages.pageNumber"  # Optional. The fields to return in the Document object.
# processor_version_id = "YOUR_PROCESSOR_VERSION_ID" # Optional. Processor version to use


def processDocument( filePath
) -> None:
    
    # You must set the `api_endpoint` if you use a location other than "us".

    project_id="1019612266116"
    location="us"
    processor_id="90df0be851ba5b42"
    field_mask="text,entities"
    file_path=filePath
    processor_version_id: Optional[str] = None
    #determine the mime type
    mime_type = magic.from_file(file_path, mime=True)
    #print("The mime value is :", mime_type)
    if mime_type == "":
        print("Not a valid file:", file_path)
        return
    
    opts = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")

    client = documentai.DocumentProcessorServiceClient(client_options=opts)

    if processor_version_id:
        # The full resource name of the processor version, e.g.:
        # `projects/{project_id}/locations/{location}/processors/{processor_id}/processorVersions/{processor_version_id}`
        name = client.processor_version_path(project_id, location, processor_id, processor_version_id)
    else:
        # The full resource name of the processor, e.g.:
        # `projects/{project_id}/locations/{location}/processors/{processor_id}`
        name = client.processor_path(project_id, location, processor_id)

    # Read the file into memory
    with open(file_path, "rb") as fileProcessed:
        file_content = fileProcessed.read()

    # Load binary data
    raw_document = documentai.RawDocument(content=file_content, mime_type=mime_type)

    # For more information: https://cloud.google.com/document-ai/docs/reference/rest/v1/ProcessOptions
    # Optional: Additional configurations for processing.
    #process_options = documentai.ProcessOptions(
    #    # Process only specific pages
    #    individual_page_selector=documentai.ProcessOptions.IndividualPageSelector(
    #        pages=[1]
    #    )
    #)

    # Configure the process request
    request = documentai.ProcessRequest(
        name=name,
        raw_document=raw_document,
        field_mask=field_mask,
#        process_options=process_options,
    )

    result = client.process_document(request=request)
    # Convert the protobuf message to a dictionary
    document = MessageToDict(result.document._pb)
   
# Extract the text
    result = {
        "entities": []
    }
   
    # Extract required entity fields
    for entity in document.get("entities", []):
        result["entities"].append({
            "type": entity.get("type", ""),
            "mentionText": entity.get("mentionText", ""),
            "confidence": entity.get("confidence", 0)
        })
   
    return result  # type: ignore

