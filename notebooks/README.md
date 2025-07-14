# Notebooks

This folder contains the R Markdown files (.Rmd) used for modeling and forecasting AAA Washington's emergency roadside call volume. Each notebook represents a distinct analytical phase in the project:

- **Phase 1: Temperature-Based Regression**  
  Uses average daily temperature to explain variation in call volume via linear regression.

- **Phase 2: ARIMA Modeling**  
  Applies Box-Jenkins (ARIMA) methods to capture autocorrelation and seasonal patterns in call volume.

- **Phase 3: Multivariate ADL Modeling**  
  Combines transformed temperature and lagged unemployment rate to build an autoregressive distributed lag model for improved forecasting.

Each notebook is self-contained with code, visualizations, statistical interpretation, and model diagnostics.

## How to Run

To run the notebooks in this project:

1. **Install R and RStudio**  
   Make sure you have [R](https://cran.r-project.org/) and [RStudio](https://posit.co/download/rstudio-desktop/) installed.

2. **Install Required Packages**  
   You can install the necessary R packages using the following code:

   ```r
   install.packages(c("forecast", "ggplot2", "lmtest"))
   ```

3. **Ensure Data Files Are Available**
   Save the data file to the same directory as the .Rmd file. Set the working directory in RStudio to the same place where the files are saved.
   
4. **Run the .Rmd File**
   Open the .Rmd file in RStudio and run each code interactively or "Run All"
