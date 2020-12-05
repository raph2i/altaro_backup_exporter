# Altaro Backup Exporter

### Install
download from releases page and get it running as windows-service via [nssm](https://nssm.cc)

```
nssm.exe install "altaro_backup_exporter" "C:\prometheus\altaro_backup_exporter\altaro_backup_exporter.exe"
``` 

### Configure
change the settings in config.json to your needs

Port is 13337, until we get an official portnumber


### Metrics
All metrics have this labels:
` hostname,vmname,vmuuid `

metrics:
```
altaro_lastoffsitecopy_result
altaro_lastbackup_result
altaro_lastoffsitecopy_transfersize_uncompressed_bytes
altaro_lastoffsitecopy_transfersize_compressed_bytes
altaro_lastbackup_transfersize_uncompressed_bytes
altaro_lastbackup_transfersize_compressed_bytes
altaro_lastoffsitecopy_duration_seconds
altaro_lastbackup_duration_seconds
altaro_lastoffsitecopy_timestamp
altaro_lastbackup_timestamp
```

### License
MIT // 2020 - Raphael Pertl