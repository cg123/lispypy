(define area (lambda (r) (* 3.141592653 (* r r))))
(display "The area of a circle with radius 3 is" (area 3) ".")

(defmacro defun (name args exp)
	(define name (lambda args exp)))

(defun x2 (n)
	(+ n n))

(display (x2 3))
(display (equal 18 (x2 9)))
