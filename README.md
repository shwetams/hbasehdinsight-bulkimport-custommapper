---
  services: hdinsight
  platforms: java
  author: shwetams
---
# Bulk import data with HBase on HDInsight

Hbase is clearly one of the most reliable, economical large scale NoSQL store. One of the challenges of deploying an HBase store is importing large amounts of data into HBase. This is a very common requirement, as most of the HBase use cases are extending an existing data system to scale.

HBase has an in-built tool call ImportTsv that can be used for importing data in csv files. You can specify the seperator, the column families and column keys in the parameters.

Following is an example of the standard importer.


` hbase org.apache.hadoop.hbase.mapreduce.ImportTsv -Dimporttsv.separator='|' -Dimporttsv.columns=HBASE_ROW_KEY,temperature:in,temperature:out,pressure:high,pressure:low,description:val sensor /tempdata/importdata.csv`

You can get more details on using the default importer at this [http://hbase.apache.org/book.html#importtsv](http://hbase.apache.org/book.html#importtsv).

A key point to note is if you specify the parameter : `-Dimporttsv.bulk.output` the ImportTsv will not insert data into HBase, but create an HFile that can be bulk uploaded into HBase using the `hbase org.apache.hadoop.hbase.mapreduce.LoadIncrementalHFiles ` command line tool.

This is recommended approach for bulk import of data.

However, the default ImportTsv importer expects a specific file format. Often, the existing file formats may not exactly comply with it.

ImportTsv has an option to provide a custom mapper. If a custom mapper is not provided it uses the default mapper [TsvImporterMapper.java github ](https://github.com/apache/hbase/blob/master/hbase-server/src/main/java/org/apache/hadoop/hbase/mapreduce/TsvImporterMapper.java).

You can replace this with your own custom mapper that conforms to your file format.

## Create custom mapper ##

You can write any Java based mapper to suit your requirements. For example, the mapper might extract data from a NoSQL source such as DocumentDB and create an HFile for import. Documentation on an HFile structure can be found [HBase File Format with Inline Blocks (version 2)](http://hbase.apache.org/0.94/book/apes03.html).

For my use case I decided to modify the existing TsvImporterMapper.java , as I needed a very simple change for my scenario to work. I didn't want to re-writing the mapper completely. This is in compliance with the Apache license.

 I renamed it to [DyncamicColumImporter.java](/DynamicColumnImporter.java). Refer to line number 437 for the change in code.

 ## Install custom mapper on your HBase HDInsight cluster ##

 Upload the custom mapper into your HDInsight cluster on a location of your choice. I created a directory called 'customimportmappers'

 Use the hbase classpath to add your custom importer to the hbase jar files.

 `javac -cp 'hbase classpath' -d customimportmappers DynamicColumnImporter.java`

Once this command is run, assuming the java mapper has no compile errors. Following directory structure will be created within the customimportmappers directory:

`/org/apache/hadoop/hbase/mapreduce` , the compiled DynamicColumnImporter.class file be stored in this directory path.

## Using the custom importer mapper in ImportTsv ##

Once you have successfully compiled and installed the custom mapper as described above, you can pass this class name as a parameter in the ImportTsv utility.



`hbase org.apache.hadoop.hbase.mapreduce.ImportTsv -Dimporttsv.separator='|' -Dimporttsv.mapper.class=org.apache.hadoop.hbase.mapreduce.<custom mapper name> -Dimporttsv.columns=HBASE_ROW_KEY,<column family>:<column qualifier> -Dimporttsv.bulk.output=<output hadoop file path> <hbase table name> <input csv file hadoop path>`


For example:

`hbase org.apache.hadoop.hbase.mapreduce.ImportTsv -Dimporttsv.separator='|' -Dimporttsv.mapper.class=org.apache.hadoop.hbase.mapreduce.DynamicColumnImporter -Dimporttsv.columns=HBASE_ROW_KEY,colfam1:d1,colfam2:d2 -Dimporttsv.bulk.output=/hfileout/data/ demo_table /input/part-00000 `

>Our example, I did a very quick edit of the existing mapper, where I did not really change the parameter validation code. Hence I am passing a dummy column qualifier. If you go through line number 437, the KeyValue generator does not read the qualifier from the parameter object, but from the file column itself.


This will create the required HFiles. You can then use the
`hbase org.apache.hadoop.hbase.mapreduce.LoadIncrementalHFiles` tool to import the data into HBase.

For example, the commandline below will import the HFile generated out of my custom mapper into Hbase demo_table:

 `hbase org.apache.hadoop.hbase.mapreduce.LoadIncrementalHFiles /input/part-00000 demo_table`


# Contributing

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.
