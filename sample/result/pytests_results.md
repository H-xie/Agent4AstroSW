============================= test session starts ==============================
platform darwin -- Python 3.14.2, pytest-9.1.1, pluggy-1.6.0 -- ~/.venv/bin/python
cachedir: .pytest_cache
rootdir: ~/sample/camera_calibration
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 55 items

tests/test_core.py::TestCameraCalibrator::test_initialization PASSED [ 1%]
tests/test_core.py::TestCameraCalibrator::test_custom_initialization PASSED [ 3%]
tests/test_core.py::TestCameraCalibrator::test_load_data PASSED [ 5%]
tests/test_core.py::TestCameraCalibrator::test_load_data_mismatched_sizes PASSED [ 7%]
tests/test_core.py::TestCameraCalibrator::test_load_data_wrong_columns PASSED [ 9%]
tests/test_core.py::TestCameraCalibrator::test_fit_projection_requires_data PASSED [ 10%]
tests/test_core.py::TestCameraCalibrator::test_fit_projection PASSED [ 12%]
tests/test_core.py::TestCameraCalibrator::test_fit_distortion_requires_projection PASSED [ 14%]
tests/test_core.py::TestCameraCalibrator::test_fit_distortion PASSED [ 16%]
tests/test_core.py::TestCameraCalibrator::test_global_fit_requires_distortion PASSED [ 18%]
tests/test_core.py::TestCameraCalibrator::test_global_fit PASSED [ 20%]
tests/test_core.py::TestCameraCalibrator::test_predict_requires_global_fit PASSED [ 21%]
tests/test_core.py::TestCameraCalibrator::test_predict PASSED [ 23%]
tests/test_core.py::TestCameraCalibrator::test_evaluate PASSED [ 25%]
tests/test_core.py::TestCameraCalibrator::test_get_calibration_params PASSED [ 27%]
tests/test_core.py::TestCameraCalibrator::test_calibration_workflow PASSED [ 29%]
tests/test_core.py::TestCalibratorRobustness::test_single_point PASSED [ 30%]
tests/test_core.py::TestCalibratorRobustness::test_duplicate_points PASSED [ 32%]
tests/test_core.py::TestCalibratorRobustness::test_collinear_points FAILED [ 34%]
tests/test_distortion.py::TestRhoProjection::test_linear_projection PASSED [ 36%]
tests/test_distortion.py::TestRhoProjection::test_polynomial_projection PASSED [ 38%]
tests/test_distortion.py::TestRhoProjection::test_zero_projection PASSED [ 40%]
tests/test_distortion.py::TestRhoProjection::test_batch_processing PASSED [ 41%]
tests/test_distortion.py::TestDistortionTerm::test_pure_radial_distortion FAILED [ 43%]
tests/test_distortion.py::TestDistortionTerm::test_pure_tangential_distortion PASSED [ 45%]
tests/test_distortion.py::TestDistortionTerm::test_multiplicative_nature PASSED [ 47%]
tests/test_distortion.py::TestApplyRhoDistortion::test_undistorted_rho_unchanged PASSED [ 49%]
tests/test_distortion.py::TestApplyRhoDistortion::test_rho_distortion_sign PASSED [ 50%]
tests/test_distortion.py::TestApplyRhoDistortion::test_batch_rho_distortion PASSED [ 52%]
tests/test_distortion.py::TestApplyThetaDistortion::test_undistorted_theta_unchanged PASSED [ 54%]
tests/test_distortion.py::TestApplyThetaDistortion::test_theta_modulo_2pi PASSED [ 56%]
tests/test_distortion.py::TestApplyThetaDistortion::test_batch_theta_distortion PASSED [ 58%]
tests/test_distortion.py::TestDistortionCombinations::test_small_distortion_approximation PASSED [ 60%]
tests/test_distortion.py::TestDistortionCombinations::test_symmetric_distortion PASSED [ 61%]
tests/test_integration.py::TestEndToEndCalibration::test_full_calibration_workflow FAILED [ 63%]
tests/test_integration.py::TestEndToEndCalibration::test_calibration_parameters_recovery PASSED [ 65%]
tests/test_integration.py::TestEndToEndCalibration::test_prediction_accuracy FAILED [ 67%]
tests/test_integration.py::TestIOOperations::test_calibration_params_round_trip PASSED [ 69%]
tests/test_integration.py::TestIOOperations::test_result_saving PASSED [ 70%]
tests/test_integration.py::TestIOOperations::test_evaluation_summary_saving PASSED [ 72%]
tests/test_integration.py::TestDataConsistency::test_forward_backward_consistency PASSED [ 74%]
tests/test_integration.py::TestDataConsistency::test_coordinate_system_independence PASSED [ 76%]
tests/test_projections.py::TestAzaltToPolar::test_zenith_point PASSED [ 78%]
tests/test_projections.py::TestAzaltToPolar::test_horizon_point FAILED [ 80%]
tests/test_projections.py::TestAzaltToPolar::test_batch_conversion PASSED [ 81%]
tests/test_projections.py::TestAzaltToPolar::test_north_bias_application PASSED [ 83%]
tests/test_projections.py::TestAzaltToPolar::test_scale_factor PASSED [ 85%]
tests/test_projections.py::TestPhotoToPolar::test_center_point PASSED [ 87%]
tests/test_projections.py::TestPhotoToPolar::test_cardinal_directions PASSED [ 89%]
tests/test_projections.py::TestPhotoToPolar::test_batch_conversion PASSED [ 90%]
tests/test_projections.py::TestPolarToPhoto::test_round_trip_conversion PASSED [ 92%]
tests/test_projections.py::TestPolarToAzalt::test_round_trip_conversion PASSED [ 94%]
tests/test_projections.py::TestPolarToAzalt::test_zenith_altitude PASSED [ 96%]
tests/test_projections.py::TestCoordinateChaining::test_azalt_to_photo_chain PASSED [ 98%]
tests/test_projections.py::TestCoordinateChaining::test_full_round_trip PASSED [100%]

=================================== FAILURES ===================================
**\*\***\_\_\_\_**\*\*** TestCalibratorRobustness.test_collinear_points **\*\***\_\_\_\_**\*\***

self = <tests.test_core.TestCalibratorRobustness object at 0x10d26a060>

    def test_collinear_points(self):
        """Test with collinear points."""
        cal = CameraCalibrator()
        # All points along azimuth=0
        azalt = np.array([[0, 30], [0, 45], [0, 60], [0, 75]])
        photo = np.array([[1053, 1163], [1053, 1220], [1053, 1280], [1053, 1320]])

        cal.load_data(azalt, photo)

>       cal.fit_projection()

tests/test_core.py:248:

---

src/camera*calibration/core.py:125: in fit_projection
popt, * = curve_fit(

---

f = <function CameraCalibrator.fit_projection.<locals>.projection_func at 0x10d391900>
xdata = array([655.33333333, 491.5 , 327.66666667, 163.83333333])
ydata = array([100., 157., 217., 257.]), p0 = array([1., 1., 1., 1., 1.])
sigma = None, absolute_sigma = False, check_finite = True, bounds = (-inf, inf)
method = 'lm', jac = None, full_output = False, nan_policy = None
kwargs = {'maxfev': 5000}

    def curve_fit(f, xdata, ydata, p0=None, sigma=None, absolute_sigma=False,
                  check_finite=None, bounds=(-np.inf, np.inf), method=None,
                  jac=None, *, full_output=False, nan_policy=None,
                  **kwargs):
        """
        Use non-linear least squares to fit a function, f, to data.

        Assumes ``ydata = f(xdata, *params) + eps``.

        Parameters
        ----------
        f : callable
            The model function, f(x, ...). It must take the independent
            variable as the first argument and the parameters to fit as
            separate remaining arguments.
        xdata : array_like
            The independent variable where the data is measured.
            Should usually be an M-length sequence or an (k,M)-shaped array for
            functions with k predictors, and each element should be float
            convertible if it is an array like object.
        ydata : array_like
            The dependent data, a length M array - nominally ``f(xdata, ...)``.
        p0 : array_like, optional
            Initial guess for the parameters (length N). If None, then the
            initial values will all be 1 (if the number of parameters for the
            function can be determined using introspection, otherwise a
            ValueError is raised).
        sigma : None or scalar or M-length sequence or MxM array, optional
            Determines the uncertainty in `ydata`. If we define residuals as
            ``r = ydata - f(xdata, *popt)``, then the interpretation of `sigma`
            depends on its number of dimensions:

            - A scalar or 1-D `sigma` should contain values of standard deviations of
              errors in `ydata`. In this case, the optimized function is
              ``chisq = sum((r / sigma) ** 2)``.

            - A 2-D `sigma` should contain the covariance matrix of
              errors in `ydata`. In this case, the optimized function is
              ``chisq = r.T @ inv(sigma) @ r``.

              .. versionadded:: 0.19

            None (default) is equivalent of 1-D `sigma` filled with ones.
        absolute_sigma : bool, optional
            If True, `sigma` is used in an absolute sense and the estimated parameter
            covariance `pcov` reflects these absolute values.

            If False (default), only the relative magnitudes of the `sigma` values matter.
            The returned parameter covariance matrix `pcov` is based on scaling
            `sigma` by a constant factor. This constant is set by demanding that the
            reduced `chisq` for the optimal parameters `popt` when using the
            *scaled* `sigma` equals unity. In other words, `sigma` is scaled to
            match the sample variance of the residuals after the fit. Default is False.
            Mathematically,
            ``pcov(absolute_sigma=False) = pcov(absolute_sigma=True) * chisq(popt)/(M-N)``
        check_finite : bool, optional
            If True, check that the input arrays do not contain nans of infs,
            and raise a ValueError if they do. Setting this parameter to
            False may silently produce nonsensical results if the input arrays
            do contain nans. Default is True if `nan_policy` is not specified
            explicitly and False otherwise.
        bounds : 2-tuple of array_like or `Bounds`, optional
            Lower and upper bounds on parameters. Defaults to no bounds.
            There are two ways to specify the bounds:

            - Instance of `Bounds` class.

            - 2-tuple of array_like: Each element of the tuple must be either
              an array with the length equal to the number of parameters, or a
              scalar (in which case the bound is taken to be the same for all
              parameters). Use ``np.inf`` with an appropriate sign to disable
              bounds on all or some parameters.

        method : {'lm', 'trf', 'dogbox'}, optional
            Method to use for optimization. See `least_squares` for more details.
            Default is 'lm' for unconstrained problems and 'trf' if `bounds` are
            provided. The method 'lm' won't work when the number of observations
            is less than the number of variables, use 'trf' or 'dogbox' in this
            case.

            .. versionadded:: 0.17
        jac : callable, str or None, optional
            Function with signature ``jac(x, ...)`` which computes the Jacobian
            matrix of the model function with respect to parameters as a dense
            array_like structure. It will be scaled according to provided `sigma`.
            If None (default), the Jacobian will be estimated numerically.
            String keywords for 'trf' and 'dogbox' methods can be used to select
            a finite difference scheme, see `least_squares`.

            .. versionadded:: 0.18
        full_output : bool, optional
            If True, this function returns additional information: `infodict`,
            `mesg`, and `ier`.

            .. versionadded:: 1.9
        nan_policy : {'raise', 'omit', None}, optional
            Defines how to handle when input contains nan.
            The following options are available (default is None):

            * 'raise': throws an error
            * 'omit': performs the calculations ignoring nan values
            * None: no special handling of NaNs is performed
              (except what is done by check_finite); the behavior when NaNs
              are present is implementation-dependent and may change.

            Note that if this value is specified explicitly (not None),
            `check_finite` will be set as False.

            .. versionadded:: 1.11
        **kwargs
            Keyword arguments passed to `leastsq` for ``method='lm'`` or
            `least_squares` otherwise.

        Returns
        -------
        popt : array
            Optimal values for the parameters so that the sum of the squared
            residuals of ``f(xdata, *popt) - ydata`` is minimized.
        pcov : 2-D array
            The estimated approximate covariance of popt. The diagonals provide
            the variance of the parameter estimate. To compute one standard
            deviation errors on the parameters, use
            ``perr = np.sqrt(np.diag(pcov))``. Note that the relationship between
            `cov` and parameter error estimates is derived based on a linear
            approximation to the model function around the optimum [1]_.
            When this approximation becomes inaccurate, `cov` may not provide an
            accurate measure of uncertainty.

            How the `sigma` parameter affects the estimated covariance
            depends on `absolute_sigma` argument, as described above.

            If the Jacobian matrix at the solution doesn't have a full rank, then
            'lm' method returns a matrix filled with ``np.inf``, on the other hand
            'trf'  and 'dogbox' methods use Moore-Penrose pseudoinverse to compute
            the covariance matrix. Covariance matrices with large condition numbers
            (e.g. computed with `numpy.linalg.cond`) may indicate that results are
            unreliable.
        infodict : dict (returned only if `full_output` is True)
            a dictionary of optional outputs with the keys:

            ``nfev``
                The number of function calls. Methods 'trf' and 'dogbox' do not
                count function calls for numerical Jacobian approximation,
                as opposed to 'lm' method.
            ``fvec``
                The residual values evaluated at the solution, for a 1-D `sigma`
                this is ``(f(x, *popt) - ydata)/sigma``.
            ``fjac``
                A permutation of the R matrix of a QR
                factorization of the final approximate
                Jacobian matrix, stored column wise.
                Together with ipvt, the covariance of the
                estimate can be approximated.
                Method 'lm' only provides this information.
            ``ipvt``
                An integer array of length N which defines
                a permutation matrix, p, such that
                fjac*p = q*r, where r is upper triangular
                with diagonal elements of nonincreasing
                magnitude. Column j of p is column ipvt(j)
                of the identity matrix.
                Method 'lm' only provides this information.
            ``qtf``
                The vector (transpose(q) * fvec).
                Method 'lm' only provides this information.

            .. versionadded:: 1.9
        mesg : str (returned only if `full_output` is True)
            A string message giving information about the solution.

            .. versionadded:: 1.9
        ier : int (returned only if `full_output` is True)
            An integer flag. If it is equal to 1, 2, 3 or 4, the solution was
            found. Otherwise, the solution was not found. In either case, the
            optional output variable `mesg` gives more information.

            .. versionadded:: 1.9

        Raises
        ------
        ValueError
            if either `ydata` or `xdata` contain NaNs, or if incompatible options
            are used.

        RuntimeError
            if the least-squares minimization fails.

        TypeError
            if the number of data points is fewer than the number of parameters

        OptimizeWarning
            if covariance of the parameters can not be estimated.

        See Also
        --------
        least_squares : Minimize the sum of squares of nonlinear functions.
        scipy.stats.linregress : Calculate a linear least squares regression for
                                 two sets of measurements.

        Notes
        -----
        Users should ensure that inputs `xdata`, `ydata`, and the output of `f`
        are ``float64``, or else the optimization may return incorrect results.

        With ``method='lm'``, the algorithm uses the Levenberg-Marquardt algorithm
        through `leastsq`. Note that this algorithm can only deal with
        unconstrained problems.

        Box constraints can be handled by methods 'trf' and 'dogbox'. Refer to
        the docstring of `least_squares` for more information.

        Parameters to be fitted must have similar scale. Differences of multiple
        orders of magnitude can lead to incorrect results. For the 'trf' and
        'dogbox' methods, the `x_scale` keyword argument can be used to scale
        the parameters.

        `curve_fit` is for local optimization of parameters to minimize the sum of squares
        of residuals. For global optimization, other choices of objective function, and
        other advanced features, consider using SciPy's :ref:`tutorial_optimize_global`
        tools or the `LMFIT <https://lmfit.github.io/lmfit-py/index.html>`_ package.

        References
        ----------
        .. [1] K. Vugrin et al. Confidence region estimation techniques for nonlinear
               regression in groundwater flow: Three case studies. Water Resources
               Research, Vol. 43, W03423, :doi:`10.1029/2005WR004804`

        Examples
        --------
        >>> import numpy as np
        >>> import matplotlib.pyplot as plt
        >>> from scipy.optimize import curve_fit

        >>> def func(x, a, b, c):
        ...     return a * np.exp(-b * x) + c

        Define the data to be fit with some noise:

        >>> xdata = np.linspace(0, 4, 50)
        >>> y = func(xdata, 2.5, 1.3, 0.5)
        >>> rng = np.random.default_rng()
        >>> y_noise = 0.2 * rng.normal(size=xdata.size)
        >>> ydata = y + y_noise
        >>> plt.plot(xdata, ydata, 'b-', label='data')

        Fit for the parameters a, b, c of the function `func`:

        >>> popt, pcov = curve_fit(func, xdata, ydata)
        >>> popt
        array([2.56274217, 1.37268521, 0.47427475])
        >>> plt.plot(xdata, func(xdata, *popt), 'r-',
        ...          label='fit: a=%5.3f, b=%5.3f, c=%5.3f' % tuple(popt))

        Constrain the optimization to the region of ``0 <= a <= 3``,
        ``0 <= b <= 1`` and ``0 <= c <= 0.5``:

        >>> popt, pcov = curve_fit(func, xdata, ydata, bounds=(0, [3., 1., 0.5]))
        >>> popt
        array([2.43736712, 1.        , 0.34463856])
        >>> plt.plot(xdata, func(xdata, *popt), 'g--',
        ...          label='fit: a=%5.3f, b=%5.3f, c=%5.3f' % tuple(popt))

        >>> plt.xlabel('x')
        >>> plt.ylabel('y')
        >>> plt.legend()
        >>> plt.show()

        For reliable results, the model `func` should not be overparametrized;
        redundant parameters can cause unreliable covariance matrices and, in some
        cases, poorer quality fits. As a quick check of whether the model may be
        overparameterized, calculate the condition number of the covariance matrix:

        >>> np.linalg.cond(pcov)
        34.571092161547405  # may vary

        The value is small, so it does not raise much concern. If, however, we were
        to add a fourth parameter ``d`` to `func` with the same effect as ``a``:

        >>> def func2(x, a, b, c, d):
        ...     return a * d * np.exp(-b * x) + c  # a and d are redundant
        >>> popt, pcov = curve_fit(func2, xdata, ydata)
        >>> np.linalg.cond(pcov)
        1.13250718925596e+32  # may vary

        Such a large value is cause for concern. The diagonal elements of the
        covariance matrix, which is related to uncertainty of the fit, gives more
        information:

        >>> np.diag(pcov)
        array([1.48814742e+29, 3.78596560e-02, 5.39253738e-03, 2.76417220e+28])  # may vary

        Note that the first and last terms are much larger than the other elements,
        suggesting that the optimal values of these parameters are ambiguous and
        that only one of these parameters is needed in the model.

        If the optimal parameters of `f` differ by multiple orders of magnitude, the
        resulting fit can be inaccurate. Sometimes, `curve_fit` can fail to find any
        results:

        >>> ydata = func(xdata, 500000, 0.01, 15)
        >>> try:
        ...     popt, pcov = curve_fit(func, xdata, ydata, method = 'trf')
        ... except RuntimeError as e:
        ...     print(e)
        Optimal parameters not found: The maximum number of function evaluations is
        exceeded.

        If parameter scale is roughly known beforehand, it can be defined in
        `x_scale` argument:

        >>> popt, pcov = curve_fit(func, xdata, ydata, method = 'trf',
        ...                        x_scale = [1000, 1, 1])
        >>> popt
        array([5.00000000e+05, 1.00000000e-02, 1.49999999e+01])
        """
        if p0 is None:
            # determine number of parameters by inspecting the function
            sig = _getfullargspec(f)
            args = sig.args
            if len(args) < 2:
                raise ValueError("Unable to determine number of fit parameters.")
            n = len(args) - 1
        else:
            p0 = np.atleast_1d(p0)
            n = p0.size

        if isinstance(bounds, Bounds):
            lb, ub = bounds.lb, bounds.ub
        else:
            lb, ub = prepare_bounds(bounds, n)
        if p0 is None:
            p0 = _initialize_feasible(lb, ub)

        bounded_problem = np.any((lb > -np.inf) | (ub < np.inf))
        if method is None:
            if bounded_problem:
                method = 'trf'
            else:
                method = 'lm'

        if method == 'lm' and bounded_problem:
            raise ValueError("Method 'lm' only works for unconstrained problems. "
                             "Use 'trf' or 'dogbox' instead.")

        if check_finite is None:
            check_finite = True if nan_policy is None else False

        # optimization may produce garbage for float32 inputs, cast them to float64
        if check_finite:
            ydata = np.asarray_chkfinite(ydata, float)
        else:
            ydata = np.asarray(ydata, float)

        if isinstance(xdata, list | tuple | np.ndarray):
            # `xdata` is passed straight to the user-defined `f`, so allow
            # non-array_like `xdata`.
            if check_finite:
                xdata = np.asarray_chkfinite(xdata, float)
            else:
                xdata = np.asarray(xdata, float)

        if ydata.size == 0:
            raise ValueError("`ydata` must not be empty!")

        # nan handling is needed only if check_finite is False because if True,
        # the x-y data are already checked, and they don't contain nans.
        if not check_finite and nan_policy is not None:
            if nan_policy == "propagate":
                msg = "`nan_policy='propagate'` is not supported by this function."
                raise ValueError(msg)
            if nan_policy not in ("raise", "omit"):
                # Override error message raised by _contains_nan
                msg = "nan_policy must be one of {None, 'raise', 'omit'}"
                raise ValueError(msg)

            x_contains_nan = _contains_nan(xdata, nan_policy)
            y_contains_nan = _contains_nan(ydata, nan_policy)

            if (x_contains_nan or y_contains_nan) and nan_policy == 'omit':
                # ignore NaNs for N dimensional arrays
                has_nan = np.isnan(xdata)
                has_nan = has_nan.any(axis=tuple(range(has_nan.ndim-1)))
                has_nan |= np.isnan(ydata)

                xdata = xdata[..., ~has_nan]
                ydata = ydata[~has_nan]

                # Also omit the corresponding entries from sigma
                if sigma is not None:
                    sigma = np.asarray(sigma)
                    if sigma.ndim == 1:
                        sigma = sigma[~has_nan]
                    elif sigma.ndim == 2:
                        sigma = sigma[~has_nan, :]
                        sigma = sigma[:, ~has_nan]

        # Determine type of sigma
        if sigma is not None:
            sigma = np.asarray(sigma)

            # if 1-D or a scalar, sigma are errors, define transform = 1/sigma
            if sigma.size == 1 or sigma.shape == (ydata.size,):
                transform = 1.0 / sigma
            # if 2-D, sigma is the covariance matrix,
            # define transform = L such that L L^T = C
            elif sigma.shape == (ydata.size, ydata.size):
                try:
                    # scipy.linalg.cholesky requires lower=True to return L L^T = A
                    transform = cholesky(sigma, lower=True)
                except LinAlgError as e:
                    raise ValueError("`sigma` must be positive definite.") from e
            else:
                raise ValueError("`sigma` has incorrect shape.")
        else:
            transform = None

        func = _lightweight_memoizer(_wrap_func(f, xdata, ydata, transform))

        if callable(jac):
            jac = _lightweight_memoizer(_wrap_jac(jac, xdata, transform))
        elif jac is None and method != 'lm':
            jac = '2-point'

        if 'args' in kwargs:
            # The specification for the model function `f` does not support
            # additional arguments. Refer to the `curve_fit` docstring for
            # acceptable call signatures of `f`.
            raise ValueError("'args' is not a supported keyword argument.")

        if method == 'lm':
            # if ydata.size == 1, this might be used for broadcast.
            if ydata.size != 1 and n > ydata.size:

>               raise TypeError(f"The number of func parameters={n} must not"

                                f" exceed the number of data points={ydata.size}")

E TypeError: The number of func parameters=5 must not exceed the number of data points=4

../../.venv/lib/python3.14/site-packages/scipy/optimize/\_minpack_py.py:1022: TypeError
**\*\***\_\_\_\_**\*\*** TestDistortionTerm.test_pure_radial_distortion **\*\***\_\_\_\_**\*\***

self = <tests.test_distortion.TestDistortionTerm object at 0x10d237b10>

    def test_pure_radial_distortion(self):
        """Test with only radial component."""
        polar = np.array([[10, 0], [20, np.pi / 2]])
        radial = np.array([0.1, 0, 0])
        tangential = np.array([0, 0, 0, 0])

        result = distortion_term(polar, radial, tangential)

        # Should be proportional to rho only
        expected = radial[0] * polar[:, 0]  # r0 * rho + 0 * rho^3 + ...

>       assert np.allclose(result, expected)
>
> E assert False
> E + where False = <function allclose at 0x1071a8ab0>(array([0., 0.]), array([1., 2.]))
> E + where <function allclose at 0x1071a8ab0> = np.allclose

tests/test_distortion.py:74: AssertionError \***\*\_\_\_\_\*\*** TestEndToEndCalibration.test_full_calibration_workflow \***\*\_\_\_\_\*\***

self = <tests.test_integration.TestEndToEndCalibration object at 0x10d3187d0>
synthetic_calibration_data = (array([[250.72890682,  27.84086329],
       [103.01016058,  73.71215203],
       [ 81.66652328,  59.19890835],
      ...
       [1055.32306952, 1063.26855664]]), {'center_x': 1053, 'center_y': 1063, 'scale': 983, 'north_bias': 2.716, ...})

    def test_full_calibration_workflow(self, synthetic_calibration_data):
        """Test complete calibration pipeline."""
        azalt, photo, true_params = synthetic_calibration_data

        # Create calibrator
        cal = CameraCalibrator(
            initial_center_x=true_params["center_x"],
            initial_center_y=true_params["center_y"],
            initial_scale=true_params["scale"],
            initial_north_bias=true_params["north_bias"],
        )

        # Load data
        cal.load_data(azalt, photo)

        # Fit stages
        proj_result = cal.fit_projection()
        assert proj_result["residual_mean"] < 10  # Should fit reasonably well

        dist_result = cal.fit_distortion()
        assert dist_result["rho"]["residual_mean"] < 5

        full_params = cal.global_fit()
        assert full_params.shape == (23,)

        # Evaluate
        eval_result = cal.evaluate()

        # Check that RMS error is reasonable (noise was ~0.5 pixels)

>       assert eval_result.rms_error < 2.0
>
> E assert 3.4113148053241007 < 2.0
> E + where 3.4113148053241007 = CalibrationResult(predicted_photo_x=array([1053.45111633, 1050.84382607, 1057.73175609, 1054.27030177,\n 1053.94572139, 1053.15746916, 1050.36252053, 1052.32149564,\n 1054.65028023, 1053.67615519, 1049.70582943, 1056.28754263,\n 1054.40523424, 1051.05513724, 1056.57552481, 1053.60892942,\n 1052.6454151 , 1054.07911683, 1054.02253621, 1057.33224065,\n 1052.96512917, 1056.78884657, 1056.62068464, 1056.15761734,\n 1053.32225263, 1057.8209407 , 1051.56030941, 1053.13162937,\n 1052.30619705, 1053.25215287, 1056.05564056, 1052.01860767,\n 1052.37665998, 1051.78453314, 1055.422461 , 1056.39822137,\n 1054.29395742, 1056.65699275, 1050.61150232, 1051.93576875,\n 1054.96805314, 1052.67904531, 1055.10766675, 1050.28345292,\n 1052.84395511, 1052.91619463, 1052.7402941 , 1051.29477399,\n 1053.90586948, 1053.1029324 ]), predicted_photo_y=array([1062.76669458, 1060.91405491, 1061.47899273, 1065.06244697,\n 1059.82392298, 1059.91258665, 1059.47219768, 1064.88489427,\n 1063.49223794, 1065.40125459, 1062.15993444, 1064.51901607,\n 1057.61142254, 1065.03728966, 1061.95068106, 1064.30348049,\n 1064.88729103, 1062.77184128, 1061.09342539, 1062.17894978,\n 1060.23948277, 1063.17101417, 1064.17713838, 1059.37124815,\n 1062.40458238, 1061.17750674, 1064.99679969, 1060.49768286,\n 1061.49100615, 1064.96104087, 1061.23378169, 1058.07443723,\n 1065.29651623, 1060.31490955, 1060.9094222 , 1060.55450505,\n 1059.336837 , 1056.43516643, 1060.35243362, 1059.9984482 ,\n 1064.72224813, 1062.06686518, 1063.5384633 , 1062.43348353,\n 1066.28938144, 1057.78347039, 1061.14909452, 1064.58848546,\n 1062.28281046, 1062.5720396 ]), error_x=array([ 0.85647055, -2.13616047, 6.74996073, -2.4491555 , -0.07467698,\n -1.3813747 , -0.13287771, -3.91918101, -0.55597679, -1.1148484 ,\n -4.1215733 , 1.39815652, -0.94102205, 1.37611889, 2.85895563,\n 1.30198974, 2.37989582, 1.94441562, 0.11345474, 0.07682186,\n 2.47087167, 4.78086958, 1.79788253, -0.82500825, 4.153001 ,\n 3.93242941, -2.08947026, -0.95176035, -1.12545258, -3.52342836,\n 5.51301277, -3.65160704, -2.45983065, -3.49774152, 0.86758924,\n 2.80863612, -0.49705577, 1.26867992, -1.15154431, -4.75549061,\n -1.65038071, 1.28011999, 2.48563306, -4.9232063 , 0.87820919,\n 1.66254525, 0.63400907, 0.35817292, 0.07988482, -2.22013712]), error_y=array([ 1.20301 , 1.50759404, 1.17293366, 1.94896836, -4.6951796 ,\n -1.16721295, -4.25815299, -2.02565749, 1.8211003 , 6.70193653,\n 3.76859104, -2.47774036, -2.78046388, 1.70338239, 1.6547511 ,\n 5.37073173, 4.4455012 , 0.14140298, -1.74722814, -0.18788015,\n -1.25746076, -1.72436729, -2.29881855, -4.79534515, 3.71414276,\n 2.26622137, 5.6656845 , -3.38257797, -2.41117801, -0.30020891,\n -1.47731168, -2.21859491, 6.18710689, -1.36771484, -0.24255714,\n 0.51444052, -1.37552523, -2.40943734, -3.74060204, -1.16704582,\n 0.53977146, -0.56156956, 3.29065682, 1.56520874, -0.17756411,\n -1.83886694, -3.13454463, 0.19993932, 0.90547885, -0.69651704])).rms_error

tests/test_integration.py:113: AssertionError
**\*\***\_\_\_**\*\*** TestEndToEndCalibration.test_prediction_accuracy **\*\***\_\_\_**\*\***

self = <tests.test_integration.TestEndToEndCalibration object at 0x10d26a9e0>
synthetic_calibration_data = (array([[250.72890682,  27.84086329],
       [103.01016058,  73.71215203],
       [ 81.66652328,  59.19890835],
      ...
       [1055.32306952, 1063.26855664]]), {'center_x': 1053, 'center_y': 1063, 'scale': 983, 'north_bias': 2.716, ...})

    def test_prediction_accuracy(self, synthetic_calibration_data):
        """Test prediction accuracy on training data."""
        azalt, photo, _ = synthetic_calibration_data

        cal = CameraCalibrator()
        cal.load_data(azalt, photo)
        cal.fit_projection()
        cal.fit_distortion()
        cal.global_fit()

        predictions = cal.predict(azalt)
        errors = predictions - photo

        # Check accuracy
        rms_error = np.sqrt(np.mean(errors**2))

>       assert rms_error < 1.0  # Should be small on training data

        ^^^^^^^^^^^^^^^^^^^^^^

E assert np.float64(2.701907558855739) < 1.0

tests/test_integration.py:153: AssertionError \***\*\*\*\*\***\_\***\*\*\*\*\*** TestAzaltToPolar.test_horizon_point \***\*\*\*\*\***\_\_\***\*\*\*\*\***

self = <tests.test_projections.TestAzaltToPolar object at 0x10d318550>

    def test_horizon_point(self):
        """Test that horizon (alt=0) maps to maximum rho."""
        azalt = np.array([[0, 0]])
        polar = azalt_to_polar(azalt, scale=983.0)
        expected_rho = 983.0 * np.pi / 2  # Maximum radius

>       assert np.isclose(polar[0, 0], expected_rho, rtol=0.01)
>
> E assert np.False*
> E + where np.False* = <function isclose at 0x1071a8bf0>(np.float64(983.0), 1544.0927892393834, rtol=0.01)
> E + where <function isclose at 0x1071a8bf0> = np.isclose

tests/test_projections.py:29: AssertionError
================================ tests coverage ================================
**\*\***\_\_\_**\*\*** coverage: platform darwin, python 3.14.2-final-0 **\*\***\_\_\_**\*\***

## Name Stmts Miss Cover Missing

src/camera_calibration/**init**.py 7 0 100%
src/camera_calibration/core.py 119 4 97% 161, 236, 382, 410
src/camera_calibration/distortion.py 20 1 95% 160
src/camera_calibration/io.py 54 15 72% 47-61, 134, 191-192, 195-196
src/camera_calibration/models.py 44 13 70% 59, 63, 93, 97, 118, 143-154
src/camera_calibration/projections.py 32 0 100%

---

TOTAL 276 33 88%
=========================== short test summary info ============================
FAILED tests/test_core.py::TestCalibratorRobustness::test_collinear_points - TypeError: The number of func parameters=5 must not exceed the number of data points=4
FAILED tests/test_distortion.py::TestDistortionTerm::test_pure_radial_distortion - assert False

- where False = <function allclose at 0x1071a8ab0>(array([0., 0.]), array([1., 2.]))
- where <function allclose at 0x1071a8ab0> = np.allclose
  FAILED tests/test_integration.py::TestEndToEndCalibration::test_full_calibration_workflow - assert 3.4113148053241007 < 2.0
- where 3.4113148053241007 = CalibrationResult(predicted*photo_x=array([1053.45111633, 1050.84382607, 1057.73175609, 1054.27030177,\n 1053.94572139, 1053.15746916, 1050.36252053, 1052.32149564,\n 1054.65028023, 1053.67615519, 1049.70582943, 1056.28754263,\n 1054.40523424, 1051.05513724, 1056.57552481, 1053.60892942,\n 1052.6454151 , 1054.07911683, 1054.02253621, 1057.33224065,\n 1052.96512917, 1056.78884657, 1056.62068464, 1056.15761734,\n 1053.32225263, 1057.8209407 , 1051.56030941, 1053.13162937,\n 1052.30619705, 1053.25215287, 1056.05564056, 1052.01860767,\n 1052.37665998, 1051.78453314, 1055.422461 , 1056.39822137,\n 1054.29395742, 1056.65699275, 1050.61150232, 1051.93576875,\n 1054.96805314, 1052.67904531, 1055.10766675, 1050.28345292,\n 1052.84395511, 1052.91619463, 1052.7402941 , 1051.29477399,\n 1053.90586948, 1053.1029324 ]), predicted_photo_y=array([1062.76669458, 1060.91405491, 1061.47899273, 1065.06244697,\n 1059.82392298, 1059.91258665, 1059.47219768, 1064.88489427,\n 1063.49223794, 1065.40125459, 1062.15993444, 1064.51901607,\n 1057.61142254, 1065.03728966, 1061.95068106, 1064.30348049,\n 1064.88729103, 1062.77184128, 1061.09342539, 1062.17894978,\n 1060.23948277, 1063.17101417, 1064.17713838, 1059.37124815,\n 1062.40458238, 1061.17750674, 1064.99679969, 1060.49768286,\n 1061.49100615, 1064.96104087, 1061.23378169, 1058.07443723,\n 1065.29651623, 1060.31490955, 1060.9094222 , 1060.55450505,\n 1059.336837 , 1056.43516643, 1060.35243362, 1059.9984482 ,\n 1064.72224813, 1062.06686518, 1063.5384633 , 1062.43348353,\n 1066.28938144, 1057.78347039, 1061.14909452, 1064.58848546,\n 1062.28281046, 1062.5720396 ]), error_x=array([ 0.85647055, -2.13616047, 6.74996073, -2.4491555 , -0.07467698,\n -1.3813747 , -0.13287771, -3.91918101, -0.55597679, -1.1148484 ,\n -4.1215733 , 1.39815652, -0.94102205, 1.37611889, 2.85895563,\n 1.30198974, 2.37989582, 1.94441562, 0.11345474, 0.07682186,\n 2.47087167, 4.78086958, 1.79788253, -0.82500825, 4.153001 ,\n 3.93242941, -2.08947026, -0.95176035, -1.12545258, -3.52342836,\n 5.51301277, -3.65160704, -2.45983065, -3.49774152, 0.86758924,\n 2.80863612, -0.49705577, 1.26867992, -1.15154431, -4.75549061,\n -1.65038071, 1.28011999, 2.48563306, -4.9232063 , 0.87820919,\n 1.66254525, 0.63400907, 0.35817292, 0.07988482, -2.22013712]), error_y=array([ 1.20301 , 1.50759404, 1.17293366, 1.94896836, -4.6951796 ,\n -1.16721295, -4.25815299, -2.02565749, 1.8211003 , 6.70193653,\n 3.76859104, -2.47774036, -2.78046388, 1.70338239, 1.6547511 ,\n 5.37073173, 4.4455012 , 0.14140298, -1.74722814, -0.18788015,\n -1.25746076, -1.72436729, -2.29881855, -4.79534515, 3.71414276,\n 2.26622137, 5.6656845 , -3.38257797, -2.41117801, -0.30020891,\n -1.47731168, -2.21859491, 6.18710689, -1.36771484, -0.24255714,\n 0.51444052, -1.37552523, -2.40943734, -3.74060204, -1.16704582,\n 0.53977146, -0.56156956, 3.29065682, 1.56520874, -0.17756411,\n -1.83886694, -3.13454463, 0.19993932, 0.90547885, -0.69651704])).rms_error
  FAILED tests/test_integration.py::TestEndToEndCalibration::test_prediction_accuracy - assert np.float64(2.701907558855739) < 1.0
  FAILED tests/test_projections.py::TestAzaltToPolar::test_horizon_point - assert np.False*
- where np.False\_ = <function isclose at 0x1071a8bf0>(np.float64(983.0), 1544.0927892393834, rtol=0.01)
- where <function isclose at 0x1071a8bf0> = np.isclose
  ========================= 5 failed, 50 passed in 0.78s =========================
