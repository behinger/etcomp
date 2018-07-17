// Built with stan 2.11
data {
    int<lower=1> N;
    real D[N]; 
    vector[N] time;
}

parameters {
    vector[2] offset;
    vector[2] slope;

    real<lower=0> sigma;
}

// Marginalize out tau and
// calculate log_p(D | mu1, sd1, mu2, sd2)
// Quadratic time solution
//transformed parameters {
//      vector[N] log_p;
//      real mu;
//      real sigma;
//      log_p = rep_vector(-log(N), N);
//      for (tau in 1:N)
//        for (i in 1:N) {
//          mu = i < tau ? mu1 : mu2;
//          sigma = i < tau ? sigma1 : sigma2;
//          log_p[tau] = log_p[tau] + normal_lpdf(D[i] | mu, sigma);
//      }
//}


// Linear time solution, as suggested by @idontgetoutmuch
// https://github.com/gmodena/bayesian-changepoint/issues/1
transformed parameters {
  vector[N] log_p;
  {
    vector[N+1] log_p_e;
    vector[N+1] log_p_l;
    log_p_e[1] = 0;
    log_p_l[1] = 0;
    for (i in 1:N) {
      log_p_e[i + 1] = log_p_e[i] + normal_lpdf(D[i] | offset[1] + time * slope[1], sigma);
      log_p_l[i + 1] = log_p_l[i] + normal_lpdf(D[i] | offset[2] + time * slope[2], sigma);
    }
    log_p = rep_vector(-log(N) + log_p_l[N + 1], N) + head(log_p_e, N) - head(log_p_l, N);
  }
}

model {
    offset[1] ~ normal(0,1);
    offset[2] ~ normal(0,100);
    slope[1] ~ normal(0,1);
    slope[2] ~ normal(0,10);
    sigma ~ cauchy(0,5);
    
    target += log_sum_exp(log_p);
} 

//Draw the discrete parameter tau. This is highly inefficient
generated quantities {
    int<lower=1,upper=N> tau;
    tau = categorical_rng(softmax(log_p));
}