# This script will only edit the config.xml file.
# It will not do anything else. Copying or moving the certificates is done by a seperate script.
# You are free to use or modify this for whatever purpose. Just let me know how much time it saved you :)
import base64
import xmltodict
import secrets
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--publickey", help = "Specify the location of the public key file", required=True)
parser.add_argument("--privatekey", help= " Specify the location the private key file", required=True)
parser.add_argument("--config", help = 'Specify the location of the downloaded pfSense config', required=True)
args = parser.parse_args()

pf_config_file = args.config
pub_key_file = args.publickey
priv_key_file = args.privatekey

def read_files():
    """Load in pf config file and TLS pub and priv keys"""
    with open(pf_config_file, 'r', encoding='utf-8') as conf_file:
        r_xml = conf_file.read()
    with open(pub_key_file, 'r', encoding='utf-8') as pk:
        public_key = pk.read()
    with open(priv_key_file, 'r', encoding='utf-8') as pk:
        private_key = pk.read()
    return r_xml, public_key, private_key

def update_config(certs, public_key, private_key):
    """Update the pf config file with new TLS certs. Also change the cert the web configurator uses."""
    gen_refid = secrets.token_hex(13)[:13]
    if type(certs) == dict:

        # Just incase our originally generated cert id already exist.
        while gen_refid == pf_conf['pfsense']['cert']['refid']:
            gen_refid = secrets.token_hex(13)[:13]
        
        pf_conf['pfsense']['cert'] = [pf_conf['pfsense']['cert']]
        
        # This is our new certificate. We wont delete the old ones.
        # Maybe in the future we will.
        pf_conf['pfsense']['cert'].append({
        'refid': gen_refid,
        'descr': f'LE - {gen_refid}',
        'crt': base64.b64encode(public_key.encode('utf-8')).decode('utf-8'),
        'prv': base64.b64encode(private_key.encode('utf-8')).decode('utf-8')
        })
    else:
        # Get list of existing cert ids
        cert_ids = [cert['refid'] for cert in certs]
        
        while gen_refid in cert_ids:
            gen_refid = secrets.token_hex(13)[:13]
        pf_conf['pfsense']['cert'].append({
        'refid': gen_refid,
        'descr': f'LE - {gen_refid}',
        'crt': base64.b64encode(public_key.encode('utf-8')).decode('utf-8'),
        'prv': base64.b64encode(private_key.encode('utf-8')).decode('utf-8')
        })
    
    # Finally, we tell pfsense that it should use our new TLS certificate for the web configurator.
    pf_conf['pfsense']['system']['webgui']['ssl-certref'] = gen_refid


r_xml, public_key, private_key = read_files()

pf_conf = xmltodict.parse(r_xml)

update_config(pf_conf['pfsense']['cert'], public_key, private_key)

# Convert the dict to xml and write to disk.
xml_format = xmltodict.unparse(pf_conf, pretty=True)
with open(pf_config_file, 'w', encoding='utf-8') as new_xml:
    new_xml.write(xml_format)
