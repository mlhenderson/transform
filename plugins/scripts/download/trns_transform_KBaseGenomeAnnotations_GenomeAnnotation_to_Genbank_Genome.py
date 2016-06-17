#!/usr/bin/env python

# standard library imports
import os
import sys
import argparse
import logging
import string

# 3rd party imports
# None

# KBase imports
import biokbase.Transform.script_utils as script_utils 
import biokbase.workspace.client 

from doekbase.data_api.sequence.assembly.api import AssemblyAPI
from doekbase.data_api.annotation.genome_annotation.api import GenomeAnnotationAPI
from doekbase.data_api.taxonomy.taxon.api import TaxonAPI
from doekbase.workspace.client import Workspace
from doekbase.data_api.core import ObjectAPI
from doekbase.handle.Client import AbstractHandle as handleClient

services = {"workspace_service_url": "https://ci.kbase.us/services/ws/",
            "shock_service_url": "https://ci.kbase.us/services/shock-api/",
            "handle_service_url": "https://ci.kbase.us/services/handle_service/"}


# Download method that can be called if this module is imported
# Note the logger has different levels with which it could be run.  See: https://docs.python.org/2/library/logging.html#logging-levels
# The default level is set to INFO which includes everything except DEBUG
def transform(workspace_service_url=None, shock_service_url=None, handle_service_url=None, 
              workspace_name=None, object_name=None, object_id=None, 
              object_version_number=None, working_directory=None, output_file_name=None, 
              level=logging.INFO, logger=None):  
    """
    Converts KBaseGenomeAnnotations.GenomeAnnotation to Genbank.
    
    Args:
        workspace_service_url:  A url for the KBase Workspace service 
        shock_service_url: A url for the KBase SHOCK service.
        handle_service_url: A url for the KBase Handle Service.
        workspace_name: Name of the workspace
        object_name: Name of the GenomeAnnotation object in the workspace 
        object_id: Id of the GenomeAnnotation object in the workspace, mutually exclusive to object_name
        object_version_number: Version number of workspace object (GenomeAnnotation), defaults to most recent version
        working_directory: The working directory where the output file should be stored.
        output_file_name: The desired file name of the resulting Genbank file.
        level: Logging level, defaults to logging.INFO.
    
    Returns:
        A Genbank file containing metadata, annotations, from a GenomeAnnotation object and contig sequences from an Assembly object.
    
    Authors:
        Marcin Joachimiak
    
    """ 

    def insert_newlines(s, every):
        lines = []
        for i in xrange(0, len(s), every):
            lines.append(s[i:i+every])
        return "\n".join(lines)+"\n"


    if logger is None:
        logger = script_utils.stderrlogger(__file__)
    
    logger.info("Starting conversion of KBaseGenomeAnnotations.GenomeAnnotation to Genbank")
    token = os.environ.get("KB_AUTH_TOKEN")
    
    if not os.path.isdir(args.working_directory): 
        raise Exception("The working directory does not exist {0} does not exist".format(working_directory)) 

    logger.info("Grabbing Data.")
 
    try:

        ga_api = GenomeAnnotationAPI(services, token=token, ref=genome_ref)

        tax_api = ga_api.get_taxon()

        asm_api = ga_api.get_assembly()


        ws_client = biokbase.workspace.client.Workspace(workspace_service_url) 

        #load GenomeAnnotation
        #if object_version_number and object_name:
        #    genome_annotation = ws_client.get_objects([{"workspace":workspace_name,"name":object_name, "ver":object_version_number}])[0] 
        #elif object_name:
        #    genome_annotation = ws_client.get_objects([{"workspace":workspace_name,"name":object_name}])[0]
        #elif object_version_number and object_id:
        #    genome_annotation = ws_client.get_objects([{"workspace":workspace_name,"objid":object_id, "ver":object_version_number}])[0]
        #else:
        #    genome_annotation = ws_client.get_objects([{"workspace":workspace_name,"objid":object_id}])[0] 

        #load Assembly
        #if object_name:
        #    assembly = ws_client.get_objects([{"workspace":workspace_name,"name":object_name}])[0] 
        #elif object_id:
        #    contig_set = ws_client.get_objects([{"workspace":workspace_name,"objid":object_id}])[0]

    except Exception, e: 
        logger.exception("Unable to retrieve workspace object from {0}:{1}.".format(workspace_service_url,workspace_name))
        logger.exception(e)
        raise 

    #shock_id = None 
    #build_up_object = False
    #if "fasta_ref" in contig_set["data"]: 
    #    shock_id = contig_set["data"]["fasta_ref"] 
    #    logger.info("Trying to Retrieve data from Shock.")
    #    try:
    #        script_utils.download_file_from_shock(logger = logger, 
    #                                              shock_service_url = shock_service_url, 
    #                                              shock_id = shock_id, 
    #                                              directory = working_directory, 
    #                                              token = token)
    #    except Exception, e:
    #        logger.warning("Unable to retrive the contig set from shock.  Trying to build from the object")
    #        build_up_object = True 
    #else: 
    #    build_up_object = True

    #if build_up_object:
    ws_object_name = contig_set["info"][1]
    valid_chars = "-_.(){0}{1}".format(string.ascii_letters, string.digits)
    temp_file_name = ""
    filename_chars = list()
    
    for character in ws_object_name:
        if character in valid_chars:
            filename_chars.append(character)
        else:
            filename_chars.append("_")
    
    if len(filename_chars) == 0:
        temp_file_name = "GenbankFile"
    else:
        temp_file_name = "".join(filename_chars)

    logger.warning("The Assembly associated with this GenomeAnnotation does not have a fasta_ref to shock.  The fasta file will be attempted to be built from contig sequences in the object.")
    
    output_file = os.path.join(working_directory,temp_file_name)
    
    contig_ids = asm_api.get_contig_ids()
    contig_lengths = asm_api.get_contig_lengths(contig_ids)

    start=1
    stop=100000000

    with open(output_file, "w") as outFile:

        for c in contig_ids:

            outFile.write("LOCUS       " + c + "             " + contig_lengths[c] + " bp    " +"DNA\n")
            sn = tax_api.get_scientific_name()
            outFile.write("DEFINITION  " + sn + " genome.\n")
            outFile.write("SOURCE      " + sn + "\n")
            outFile.write("  ORGANISM  " + sn + "\n")


            region = {"contig_id": c, "start": start, "length": stop-start, "strand": "?"}
            features = get_features()

            for feat in features:
                outFile.write(">{} {}\n".format(contig["id"],contig["description"]))

        outFile.close()    
        raise IOError("The Assembly associated with this GenomeAnnotation does not have a fasta_ref to shock or sequences in the contigs. A Genbank file can not be created.  Likely dueto the ContigSet being too large.")


        #if not contig_set["data"]["contigs"]:
        #    #The contig list is empty
        #    raise Exception("This ContigSet does not have a fasta_ref to shock and does not have any contigs. Likely due to the ContigSet being too large.")

        #with open(output_file, "w") as outFile:
        #    for contig in contig_set["data"]["contigs"]:
        #        if "description" in contig:
        #            outFile.write(">{} {}\n".format(contig["id"],contig["description"]))
        #        else:
        #            outFile.write(">{}\n".format(contig["id"]))
        #    
        #        #write 80 nucleotides per line
        #        if contig["sequence"] != "":
        #            outFile.write(insert_newlines(contig["sequence"],80))
        #        else:
        #            outFile.close()    
        #            raise IOError("The Assembly associated with this GenomeAnnotation does not have a fasta_ref to shock or sequences in the contigs. A Genbank file can not be created.  Likely dueto the ContigSet being too large.")
    
    if output_file_name is not None and len(output_file_name) > 0:
        name = os.listdir(working_directory)[0]
        os.rename(os.path.join(working_directory, name), os.path.join(working_directory, output_file_name))

    logger.info("Conversion completed.")


# called only if script is run from command line
if __name__ == "__main__":
    script_details = script_utils.parse_docs(transform.__doc__)

    parser = argparse.ArgumentParser(prog=__file__, 
                                     description=script_details["Description"],
                                     epilog=script_details["Authors"])
    
    # The following 8 arguments should be fairly standard to all uploaders
    parser.add_argument("--workspace_service_url", 
                        help=script_details["Args"]["workspace_service_url"], 
                        action="store", 
                        type=str, 
                        nargs="?", 
                        required=True)
    parser.add_argument("--workspace_name", 
                        help=script_details["Args"]["workspace_name"], 
                        action="store", 
                        type=str, 
                        nargs="?", 
                        required=True)
    parser.add_argument("--working_directory", 
                        help=script_details["Args"]["working_directory"], 
                        action="store", 
                        type=str, 
                        nargs="?", 
                        required=True)

    parser.add_argument("--output_file_name", 
                        help=script_details["Args"]["output_file_name"], 
                        action="store", 
                        type=str, 
                        nargs="?", 
                        required=False)
    parser.add_argument("--object_version_number", 
                        help=script_details["Args"]["object_version_number"], 
                        action="store", 
                        type=int, 
                        nargs="?", 
                        required=False)

    object_info = parser.add_mutually_exclusive_group(required=True)
    object_info.add_argument("--object_name", 
                             help=script_details["Args"]["object_name"], 
                             action="store", 
                             type=str, 
                             nargs="?") 
    object_info.add_argument("--object_id", 
                             help=script_details["Args"]["object_id"], 
                             action="store", 
                             type=int, 
                             nargs="?")

    data_services = parser.add_mutually_exclusive_group(required=True) 
    data_services.add_argument("--shock_service_url", 
                        help=script_details["Args"]["shock_service_url"], 
                        action="store", 
                        type=str, 
                        nargs="?") 
    data_services.add_argument("--handle_service_url", 
                        help=script_details["Args"]["handle_service_url"], 
                        action="store", 
                        type=str, 
                        nargs="?")

    args = parser.parse_args()

    logger = script_utils.stderrlogger(__file__)
    logger.info("Starting download of ContigSet => FASTA")
    try:
        transform(workspace_service_url = args.workspace_service_url, 
                  shock_service_url = args.shock_service_url, 
                  handle_service_url = args.handle_service_url, 
                  workspace_name = args.workspace_name, 
                  object_name = args.object_name, 
                  object_id = args.object_id, 
                  object_version_number = args.object_version_number, 
                  output_file_name = args.output_file_name,
                  working_directory = args.working_directory, 
                  logger = logger)
    except Exception, e:
        logger.exception(e)
        sys.exit(1)
    
    sys.exit(0)

