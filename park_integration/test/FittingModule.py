#class Fitting
from sans.guitools.plottables import Data1D
from Loader import Load
from scipy import optimize
class Fitting:
    """ 
        Performs the Fit.he user determine what kind of data 
    """
    def __init__(self,data=[]):
        #self.model is a list of all models to fit
        self.model=[]
        #the list of all data to fit 
        self.data = data
        #dictionary of models parameters
        self.parameters={}
        self.contraint =None
        self.residuals=[]
        
    def fit_engine(self):
        """
            Check the contraint value and specify what kind of fit to use
        """
        return True
    def fit(self,pars, qmin=None, qmax=None):
        """
             Do the fit 
        """
        
        # Do the fit with 2 data set and one model 
        numberData= len(self.data)
        numberModel= len(self.model)
        if numberData==1 and numberModel==1:
            if qmin==None:
                xmin= min(self.data[0].x)
            if qmax==None:
                xmax= max(self.data[0].x)
           
            #chisqr, out, cov = fitHelper(self.model[0],self.data[0],pars,xmin,xmax)
            chisqr, out, cov =fitHelper(self.model[0], pars, self.data[0].x,
                                 self.data[0].y, self.data[0].dy ,xmin,xmax)
        else:# More than one data to fit with one model
            xtemp=[]
            ytemp=[]
            dytemp=[]
            for data in self.data:
                for i in range(len(data.x)):
                    if not data.x[i] in xtemp:
                        xtemp.append(data.x[i])
                       
                    if not data.y[i] in ytemp:
                        ytemp.append(data.y[i])
                        
                    if not data.dy[i] in dytemp:
                        dytemp.append(data.dy[i])
            if qmin==None:
                xmin= min(xtemp)
            if qmax==None:
                xmax= max(xtemp)      
            #chisqr, out, cov = fitHelper(self.model[0], 
            #temp,pars,min(temp.x),max(temp.x))
            chisqr, out, cov =fitHelper(self.model[0], pars, xtemp,
                                 ytemp, dytemp ,xmin,xmax)
        return chisqr, out, cov
    
    def set_model(self,model):
        """ Set model """
        self.model.append(model)
        
    def set_data(self,data):
        """ Receive plottable and create a list of data to fit"""
        self.data.append(data)
        
    def get_data(self):
        """ return list of data"""
        return self.data
    
    def add_contraint(self, contraint):
        """ User specify contraint to fit """
        self.contraint = str(contraint)
        
    def get_contraint(self):
        """ return the contraint value """
        return self.contraint
    
def get_residuals(model,data,qmin=None,qmax=None):
    """
        Calculates the vector of residuals for each point 
        in y for a given set of input parameters.
        @param params: list of parameter values
        @return: vector of residuals
    """
    residuals = []
   
    for j in range(len(data.x)):
        if data.x[j]> qmin and data.x[j]< qmax:
            residuals.append( ( data.y[j] - model.runXY(data.x[j]) ) / data.dy[j])
    
    return residuals

   
def chi2(params): 
    """
        Calculates chi^2
        @param params: list of parameter values
        @return: chi^2
    """
    sum = 0
    res = get_residuals(params)
    for item in res:
        sum += item*item
    return sum 
    
    
    def residual(self):
        return self.residuals
    
def fitHelper(model,data,pars,qmin=None,qmax=None):
    """ Do the actual fitting"""
    
    p = [param() for param in pars]
    out, cov_x, info, mesg, success = optimize.leastsq(get_residuals, p, full_output=1, warning=True)
    print info, mesg, success
    # Calculate chi squared
    if len(pars)>1:
        chisqr = self.chi2(out)
    elif len(pars)==1:
        chisqr = self.chi2([out])
        
    return chisqr, out, cov_x

class Parameter:
    """
        Class to handle model parameters
    """
    def __init__(self, model, name, value=None):
            self.model = model
            self.name = name
            if not value==None:
                self.model.setParam(self.name, value)
           
    def set(self, value):
        """
            Set the value of the parameter
        """
        self.model.setParam(self.name, value)

    def __call__(self):
        """ 
            Return the current value of the parameter
        """
        return self.model.getParam(self.name)
    
def fitHelper(model, pars, x, y, err_y ,qmin=None, qmax=None):
    """
        Fit function
        @param model: sans model object
        @param pars: list of parameters
        @param x: vector of x data
        @param y: vector of y data
        @param err_y: vector of y errors 
    """
    def f(params):
        """
            Calculates the vector of residuals for each point 
            in y for a given set of input parameters.
            @param params: list of parameter values
            @return: vector of residuals
        """
        i = 0
        for p in pars:
            p.set(params[i])
            i += 1
        
        residuals = []
        for j in range(len(x)):
            if x[j]>qmin and x[j]<qmax:
                residuals.append( ( y[j] - model.runXY(x[j]) ) / err_y[j] )
       
        return residuals
        
    def chi2(params):
        """
            Calculates chi^2
            @param params: list of parameter values
            @return: chi^2
        """
        sum = 0
        res = f(params)
        for item in res:
            sum += item*item
        return sum
        
    p = [param() for param in pars]
    out, cov_x, info, mesg, success = optimize.leastsq(f, p, full_output=1, warning=True)
    print info, mesg, success
    # Calculate chi squared
    if len(pars)>1:
        chisqr = chi2(out)
    elif len(pars)==1:
        chisqr = chi2([out])
        
    return chisqr, out, cov_x    

      
if __name__ == "__main__": 
    load= Load()
    
    # test fit one data set one model
    load.set_filename("testdata_line.txt")
    load.set_values()
    data1 = Data1D(x=[], y=[], dx=None,dy=None)
    data1.name = "data1"
    load.load_data(data1)
    Fit =Fitting()
    Fit.set_data(data1)
    from sans.guitools.LineModel import LineModel
    model  = LineModel()
    Fit.set_model(model)
    
    default_A = model.getParam('A') 
    default_B = model.getParam('B') 
    cstA = Parameter(model, 'A', default_A)
    cstB  = Parameter(model, 'B', default_B)
    
    chisqr, out, cov=Fit.fit([cstA,cstB],None,None)
    print"fit only one data",chisqr, out, cov 
    
    # test fit with 2 data and one model
    load.set_filename("testdata1.txt")
    load.set_values()
    data2 = Data1D(x=[], y=[], dx=None,dy=None)
    data2.name = "data2"
    
    load.load_data(data2)
    Fit.set_data(data2)
    
    load.set_filename("testdata2.txt")
    load.set_values()
    data3 = Data1D(x=[], y=[], dx=None,dy=None)
    data3.name = "data2"
    load.load_data(data3)
    Fit.set_data(data3)
    chisqr, out, cov=Fit.fit([cstA,cstB],None,None)
    print"fit two data",chisqr, out, cov 