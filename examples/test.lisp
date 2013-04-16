(define area (lambda (r) (* 3.141592653 (* r r))))
(display "The area of a circle with radius 3 is" (area 3) ".")

(defmacro defun (name args exp)
	(define name (lambda args exp)))

(defun factorial (n)
	(if (< n 2)
		1
		(* n (factorial (- n 1)))))

(display "10! =" (factorial 10))
