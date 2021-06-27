noi cscript "reghdfe postestimation: predict" adofile reghdfe

* Dataset
	sysuse auto
	bys turn: gen t = _n
	tsset turn t
	// drop if missing(rep)
	
	local included_e ///
		scalar: N rmse tss rss mss r2 r2_a F df_r df_m ll ll_0 ///
		matrix: b V ///
		macros: wexp wtype

* [TEST] predict after reghdfe

	local lhs price
	local rhs weight length gear disp
	local absvars turn
	fvunab tmp : `rhs'
	local K : list sizeof tmp

	* 1. Run benchmark
	areg `lhs' `rhs', absorb(`absvars')
	di e(df_a)
	local bench_df_a = e(df_a)
	storedresults save benchmark e()
	predict double xb, xb
	predict double d, d
	predict double xbd, xbd
	predict double resid, resid
	predict double dr, dr
	predict double stdp, stdp

	* AREG and REGHDFE disagree because AREG includes _cons in XB instead of D
	* VERSION 5 UPDATE: REGHDFE NOW WORKS AS AREG
	*replace xb = xb - _b[_cons]
	*replace d = d + _b[_cons]
	*replace dr = dr + _b[_cons]
	*replace stdp = stdp
	*su resid, mean

	* 2. Run reghdfe and compare
	
	reghdfe `lhs' `rhs', absorb(`absvars') keepsingletons resid verbose(-1) tol(1e-10)
	assert `bench_df_a'==e(df_a)-1
	predict double xb_test, xb
	predict double d_test, d
	predict double xbd_test, xbd
	predict double resid_test, resid
	predict double dr_test, dr
	predict double stdp_test, stdp
	su d d_test xb xb_test xbd xbd_test resid resid_test dr dr_test stdp stdp_test, sep(2)
	storedresults compare benchmark e(), tol(1e-10) include(`included_e')

	_vassert xb xb_test, tol(1e-10)
	_vassert d d_test, tol(1e-10)
	_vassert xbd xbd_test, tol(1e-10)
	_vassert resid resid_test, tol(1e-10)
	_vassert dr dr_test, tol(1e-10)

	// It's hard to make stdp match easily
	// stdp = sqrt(x_i * V * x_i')
	// _vassert stdp stdp_test, tol(1e-12)

	* Test that we can't predict resid after dropping e(resid)
	drop *_test `e(resid)'
	cap predict resid_test, resid
	assert c(rc)


storedresults drop benchmark
exit
