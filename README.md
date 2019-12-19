# Data anonymizer

Data anonymizer allows you to strip information from a dataset while preserving certain statistical properties. This is useful for data companies as it allows them to get access to data that is based on their clients' data without accessing the true data itself. Given that some transforms are non-reversible, the original data cannot be recovered.

## Getting started

* Clone the repository.
* `poetry install`.
* You can now use `data-anonymizer` as long as you are within the created virtual environment.

## Example

```csv
data-anonymizer input.csv output.csv
--feature-min-max-scale bananas celeries
--feature-binarize avocados
--feature-categorize entity carrots
--feature-remove tomatoes
--feature-anonymize carrots celeries
--feature-fill bananas 500
--feature-clamp avocados 1 3
--feature-round beets 0.15
```

An example file
```csv
date,entity,bananas,carrots,celeries,tomatoes,avocados,beets
2019-01-01,a,1,2,3,11,1,1.0
2019-02-01,a,4,5,6,15,50,1.3
2019-03-01,a,7,3,9,17,13,1.46
2019-01-01,b,1,2,3,5,6,2.67
2019-02-01,b,4,5,6,7,3,-5.66
2019-03-01,b,7,8,9,9,26,-1
```

will turn into
```
# feature-min-max-scale bananas 1 
# feature-binarize avocados 
# feature-categorize entity 0 
# feature-fill bananas 500 
# feature-clamp avocados 1 3 
# feature-round beets 0.15 
date,entity,bananas,0,1,avocados,beets
2019-01-01,C0,500,C0,0.0,1.0,1.05
2019-02-01,C0,500,C2,0.5,1.0,1.3499999999999999
2019-03-01,C0,500,C1,1.0,1.0,1.5
2019-01-01,C1,500,C0,0.0,1.0,2.6999999999999997
2019-02-01,C1,500,C2,0.5,1.0,-5.7
2019-03-01,C1,500,C3,1.0,1.0,-1.05
```
At the top of the document `data-anonymizer` adds metadata on some of the transforms that were applied to the data. Fields that have been anonymizer will be referred with their anonymized name. The metadata does not provide information that can lead to the recovery of the original data, but helps the data scientist working on the anonymized data how the transformed data came to be.

## License
The code is licensed under the [MIT license](http://choosealicense.com/licenses/mit/). See [LICENSE](LICENSE).
