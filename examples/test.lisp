(define defmacro (create-macro (name args exp)
    (define name (create-macro args exp))
))
(define area (lambda (r) (* 3.141592653 (* r r))))
(display "The area of a circle with radius 3 is" (area 3) ".")

(defmacro defun (name args exp)
	(define name (lambda args exp)))

(defun _factorial (n acc) 
    (if (equal n 0)
        acc
        (_factorial (- n 1) (* n acc))
        )
    )
(defun factorial (n) (_factorial n 1))

(display factorial)
(display "2000! =" (factorial 2000))
