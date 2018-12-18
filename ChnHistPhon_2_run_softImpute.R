library(softImpute)
DIR_RESULTS = '/path/to/ChnHistPhon/results'

# load results
characters = read.csv(paste(DIR_RESULTS, 'ChnChar.csv', sep="/"))
X  <- read.csv(paste(DIR_RESULTS, 'ChnCharData.csv', sep="/"))
Xc <- as(data.matrix(X), "Incomplete")

# run SVD softImpute
X_SVD <- softImpute(Xc, 200, type='svd', trace.it=TRUE, maxit = 200)


for (i in seq(5))
{
  loading_feature = X_SVD$v[,i][order(abs(X_SVD$v[,i]), decreasing = T)]
  names(loading_feature)  = names(X)[order(abs(X_SVD$v[,i]), decreasing = T)]

  score_characters = X_SVD$u[,i][order(abs(X_SVD$u[,i]), decreasing = T)]
  names(score_characters)  = characters$character[order(abs(X_SVD$u[,i]), decreasing = T)]

  print(loading_feature[1:10])
  print(score_characters[1:100])
}
