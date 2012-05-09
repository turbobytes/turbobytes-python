turbobytes-python
=================

Python library to access Turbobytes API


Sample usage, to purge a file

    turbobytes = TurboBytesAPI("xxxxxxxAPI_KEYxxxxxxxxxxxx", "xxxxxxxxxAPI_SECRETxxxxxxxxx")
    print turbobytes.purge("zone-name", ["/path/to/foo.jpg", "/path/to/bar.css"])
    #Show latest purges
    print turbobytes.latest_purges("zone-name")

