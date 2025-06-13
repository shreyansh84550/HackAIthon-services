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

# TODO(developer): Uncomment these variables before running the sample.
# project_id = "YOUR_PROJECT_ID"
# location = "YOUR_PROCESSOR_LOCATION" # Format is "us" or "eu"
# processor_id = "YOUR_PROCESSOR_ID" # Create processor before running sample
# file_path = "/path/to/local/pdf"
# mime_type = "application/pdf" # Refer to https://cloud.google.com/document-ai/docs/file-types for supported file types
# field_mask = "text,entities,pages.pageNumber"  # Optional. The fields to return in the Document object.
# processor_version_id = "YOUR_PROCESSOR_VERSION_ID" # Optional. Processor version to use


def processFile( filePath
) -> None:
    
    # You must set the `api_endpoint` if you use a location other than "us".
    project_id="1019612266116"
    location="us"
    processor_id="8e4b32b61de6aadc"
    file_path=filePath
    field_mask: Optional[str] = None
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
    process_options = documentai.ProcessOptions(
        # Process only specific pages
        individual_page_selector=documentai.ProcessOptions.IndividualPageSelector(
            pages=[1]
        )
    )

    # Configure the process request
    request = documentai.ProcessRequest(
        name=name,
        raw_document=raw_document,
        field_mask=field_mask,
        process_options=process_options,
    )

    result = client.process_document(request=request)

    # For a full list of `Document` object attributes, reference this page:
    # https://cloud.google.com/document-ai/docs/reference/rest/v1/Document
    document = result.document

    # Find the highest confidence value among all entities
    if document.entities :
        max_confidence = max(entity.confidence for entity in document.entities)
    else:
        max_confidence = 0
    # Filter entities to only those with the highest confidence
    highest_confidence_entities = [
        {
            "file": file_path,
            "type": entity.type_,
            "confidence": entity.confidence,
            "normalized_value": entity.normalized_value.text if entity.normalized_value else None
        }
        for entity in document.entities
        if entity.confidence == max_confidence
    ]

    if highest_confidence_entities:
        # Get the first entity (since they all have the same highest confidence)
        main_entity = highest_confidence_entities[0]
        
        if main_entity["type"] == "group-photo":
            # Call image validation function
            image_validation_result = detect_faces(file_path)
            face_count = count_faces(image_validation_result)
            image_analysis_entity = [
                {
                    "face_count": face_count
                }
            ]
            highest_confidence_entities[0]["image_analysis"] = image_analysis_entity
            print("The return from group-photo output:" , highest_confidence_entities)
            return highest_confidence_entities  # type: ignore
        #elif main_entity["type"] == "bill":
        #    # Call bill processing function
        #    bill_processing_result = detect_faces(file_path)
        #    highest_confidence_entities[0]["processing_results"] = bill_processing_result
        #    return highest_confidence_entities #type: ignore
        else:
            # Handle other entity types or return as is
            return highest_confidence_entities # type: ignore
    else:
        return None

    return highest_confidence_entities # type: ignore

# [END documentai_process_document]

