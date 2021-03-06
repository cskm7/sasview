/**
Computes the (magnetic) scattering form sld (n and m) profile
 */
#ifndef SLD2I_CLASS_H
#define SLD2I_CLASS_H

/**
 * Base class
 */
typedef struct {
	// vectors
	int is_avg;
	int n_pix;
	double* x_val;
	double* y_val;
	double* z_val;
	double* sldn_val;
	double* mx_val;
	double* my_val;
	double* mz_val;
	double* vol_pix;
    // spin ratios
    double inspin;
    double outspin;
    double stheta;
} GenI;

// Constructor
void initGenI(GenI*, int is_avg, int npix, double* x, double* y, double* z,
		double* sldn, double* mx, double* my, double* mz, double* voli,
		double in_spin, double out_spin,
		double s_theta);
// compute function
void genicomXY(GenI*, int npoints, double* qx, double* qy, double *I_out);
void genicom(GenI*, int npoints, double* q, double *I_out);

#endif
