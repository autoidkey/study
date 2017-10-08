#!/bin/sh


export ntree=500
export mtry=21

R --vanilla --slave <<EOF

rmse <- function(error) {
    sqrt(mean(error^2))
}

library(randomForest)
cates <- c("X_まとめ提示", "X_言い換え", "X_称賛", "X_発言促進", "X_挨拶", "X_御礼", "X_同意", "X_問いかけ", "X_OTHER", "X_WAIT")
set.seed(0)
data <- read.csv("$1", header=TRUE, skip=0)


feats <- names(data)
rf <- randomForest($2~.,data, ntree=$ntree, mtry=$mtry)

cat("cor all: ", cor(data\$$2,rf\$predicted), "\n")

merged <- cbind(as.matrix(data), as.vector(rf\$predicted))
colnames(merged) <- append(colnames(data), "predicted")

for (i in 1:length(cates)) {
    cate <- cates[i]
    tmp <- eval(parse(text=paste("subset(data.frame(merged), ", cate, " == 1)", sep="")))
    cat("cor ", cate, ": ", cor(tmp\$$2,tmp\$predicted), "\n")
    #if (cate != "X_まとめ提示") {
      err <- tmp\$$2 - tmp\$predicted
      cat("rmse ", cate, ": ", rmse(err), "\n")
      delta <- 1
      h <- hist(err, breaks=seq(-6.5,10.5,delta))
      pr <- h\$counts / sum(h\$counts) / delta
      pr_merged <- cbind(as.vector(h\$mid), as.vector(pr))
      write.csv(pr_merged, paste("errdist_", cate, ".csv", sep=""), row.names=FALSE)
      png(file=paste("errdist_", cate, ".png", sep=""), width=600)
      if (max(pr) < 0.5) {
        barplot(pr, names.arg=h\$mid, space=c(0,0), ylim=c(0, 0.6), yaxp=c(0, 0.6, 3), xlab="Residual error", ylab="Probability", cex=1.5, cex.axis=1.5, cey.axis=1.4, cex.lab=1.5, cey.lab=1.4)
      } else {
        barplot(pr, names.arg=h\$mid, space=c(0,0), xlab="Residual error", ylab="Probability", cex=1.5, cex.axis=1.5, cey.axis=1.4, cex.lab=1.5, cey.lab=1.4)
      }
      dev.off()

    #}
}

tmp <- subset(data.frame(merged), X_WAIT == 0)
cat("cor POST: ", cor(tmp\$$2,tmp\$predicted), "\n")
err <- tmp\$$2 - tmp\$predicted
cat("rmse POST: ", rmse(err), "\n")

err <- data\$$2 - rf\$predicted 
cat("rmse All: ", rmse(err), "\n")

min(err)
max(err)

delta <- 1
h <- hist(err, breaks=seq(-6.5,10.5,delta))
pr <- h\$counts / sum(h\$counts) / delta
pr_merged <- cbind(as.vector(h\$mid), as.vector(pr))

importance <- cbind(as.vector(feats), as.vector(rf\$importance))
write.csv(importance, "importance.csv", row.names=FALSE)

data_merged <- cbind(as.matrix(data), as.vector(rf\$predicted))
write.csv(data_merged, "predicted.csv", row.names=FALSE)

write.csv(pr_merged, "errdist.csv", row.names=FALSE, col.names=FALSE)
png(file="errdist.png", width=600)
barplot(pr, names.arg=h\$mid, space=c(0,0), ylim=c(0, 0.6), yaxp=c(0, 0.6, 3), xlab="Residual error", ylab="Probability", cex=1.5, cex.axis=1.5, cey.axis=1.4, cex.lab=1.5, cey.lab=1.4)
dev.off()

EOF



