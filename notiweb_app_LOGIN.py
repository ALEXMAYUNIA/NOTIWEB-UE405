import streamlit as st

st.set_page_config(page_title="NOTIWEB UE 405 - Huacaybamba", layout="centered", page_icon="🏥")

LOGO_B64 = "/9j/4AAQSkZJRgABAQAAAQABAAD/4gHYSUNDX1BST0ZJTEUAAQEAAAHIbGNtcwIQAABtbnRyUkdCIFhZWiAH4gADABQACQAOAB1hY3NwTVNGVAAAAABzYXdzY3RybAAAAAAAAAAAAAAAAAAA9tYAAQAAAADTLWhhbmSdkQA9QICwPUB0LIGepSKOAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAlkZXNjAAAA8AAAABxjcHJ0AAABDAAAAAx3dHB0AAABGAAAABRyWFlaAAABLAAAABRnWFlaAAABQAAAABRiWFlaAAABVAAAABRyVFJDAAABaAAAAGBnVFJDAAABaAAAAGBiVFJDAAABaAAAAGBkZXNjAAAAAAAAAAV1UkdCAAAAAAAAAAAAAAAAdGV4dAAAAABDQzAAWFlaIAAAAAAAAPNUAAEAAAABFslYWVogAAAAAAAAb6AAADjyAAADj1hZWiAAAAAAAABilgAAt4kAABjaWFlaIAAAAAAAACSgAAAPhQAAtsRjdXJ2AAAAAAAAACoAAAB8APgBnAJ1A4MEyQZOCBIKGAxiDvQRzxT2GGocLiBDJKwpai5+M+s5sz/WRldNNlR2XBdkHWyGdVZ+jYgskjacq6eMstu+mcrH12Xkd/H5////2wBDAAkGBwgHBgkICAgKCgkLDhcPDg0NDhwUFREXIh4jIyEeICAlKjUtJScyKCAgLj8vMjc5PDw8JC1CRkE6RjU7PDn/2wBDAQoKCg4MDhsPDxs5JiAmOTk5OTk5OTk5OTk5OTk5OTk5OTk5OTk5OTk5OTk5OTk5OTk5OTk5OTk5OTk5OTk5OTn/wAARCADfAOIDASIAAhEBAxEB/8QAHAABAAMBAQEBAQAAAAAAAAAAAAUGBwQDAgEI/8QAThAAAQIEAwUEBgYHBQUIAwAAAQIDAAQFEQYSIQcTMUFRImFxgRQVIzKRoUJSYnKxwTNDgpKistEWJCVT8DVjwtLhNkRFVWRzdINUk+L/xAAZAQADAQEBAAAAAAAAAAAAAAAAAQMCBAX/xAAtEQACAgEDAgUDBAMBAAAAAAAAAQIRAxIhMSJBBBMyUYFxkfAjM0JhQ6HBsf/aAAwDAQACEQMRAD8A3GEIQAIQhAAhCEACEI8Zubl5KXVMTT7bLKPeW4oJA84APaEZ1XdqUszmao8t6SofrnrpR5J4nztFXCMZY07X95cllfW9jL28NAofvGLRwurlsiEs8U6juzUani+gUwqTMVJkuJ4ttHeKB6EJvbzitTu1WmtG0pITL/2lqS2PzPyjipeyj3VVOpDTi3LIt/Er+kWeSwBhuUsTIb9X1n1lfy4fKH+lH3YrzS9kUuZ2sVL9VTpJn/3HFK/5Y407S8Sv/okSX/1sKP8AxGNOLmG6R2SqlSX2fZtn4aR5LxlhtvjWJT9ld/wjSlHtAy4S/lMzY7RMUo95DA8ZY/1j0Y2rVhP6WXpzn3UqSf5jGhpxthpXCrsDxuPxEeor+GqgMiqlTXvsuOI/AwOS7wBQl2yFNk9rKeE5SVD7TL1/koD8YsNO2iYcnTlXNLlV9JhBSP3hcfOO57C2Gqk3m9VySkq+mwkIv5ptEBUNltIe7UjMzMoroo71PwOvzjN4n2aNVmj3TLvKzUvOMh6VfafaPBbawofER7RjM3gTE9Be9Kprqn8v05Rwoct3p0J8AVR0UjaTVqa8ZWsMelbvReZO6eR4i1ie4geMDw3vB2Cz06mqNehENQMT0mvovIzQLtrqZX2XB5cx3i4iZiLTWzLppq0IQhCGIQhAAhCEACEIQAIQhAAhCEACEfK1pbQVrUEpSLkk2AjK8a7QHJxaqXQlLDalbtUy3fM6eGVu2tjwuNTy6ncMbm6RPJkjjVssuLceyNDzysoEzlQSbFAPYbP2iOfcNetooMrT8SY+nBMuuqUwlRAfc7LTXUIA4nw16mLFg7ZwnI3OV1GnvIlL/wA5H4Dz6RacR4spGF2QwspXMJSMkqzYEC2l+SR/oAxZOMOnHu/chUp9WR0vY56BgGjUgJdfbE9NJ13j4GVJ+yngPE3PfH7Xcf0KkFTaH/TH0/q5ftAeKuA+JPdFaTJYrx2d5OO+q6Or3WrEZx4aFXiqw5gRbqFguiUUIW1Kh+YT+vf7ar9RyHkBGJUnc3bNxtqsapFXTiTGuIf9jUoSUsr3XlpHDrmXYHySY+hgCu1XtV3ETigri02VLT8yAP3YvlVqcnSJNU5PO7phJAKspVqe4AmPGg1mXrskZyUbfSxnKEqdRlz24kd17jyMLzGlcVRry03UnZWJXZbQWR7VybePesIH8IESLez/AAyj/wAPUr7z7n/NHLVa9W5XGcjREmRblpxW8Q4W1qXkFyUnUAE5SL94j3p0zVP7czlPmqiXJVuWEw00GUpBSpRABNr6db6w3KfLYlHHwonscA4XP/hSf/2uf80ckxs1w277jMwz9x9R/mvEcy9iCdxtVaNK191mXlUh1Kly7TlswSrLwB0z248BEtg+vz07UalRqsloz0ir9K0LJcTe17cuR84HrW+oEsbdaSFd2Wty7hdpNZmZR08yNf3klJjz9G2h0E3afbqzCfoqUHDbvvlVfwJjQ519UtKPPoaU8ptBUG0kAqsOFzpEJRcY0eryi5lD6pZDeXP6SndhJUbAZjodehgWST3asHjhF0nRA03abLB/0WuU9+nvp945SQPFJAUPgYskxJUDFkmHFJlp5vgHUEZkdwUNQY7qhTadWJfdzsqzNNHgVJBt3g8vKKPUtn05TJj1hhaoOy7yf1C12uOgVwI7lAjvhLQ+NmN60t+pETiLZtPU9YnKI+5MJbVmSi+V5HeCLA28j4x94X2jzUk56HXUOPNJOXf5fatEcljn+PjExRNoDkvNCmYolVSM0nsl7KQk9CocgfrC48Im8S4TpWKJff3S3MqSC3NtWNxbS/JQ/wBAiKOX8cq+SSj/ACwv4J+Tm5eelm5mVeQ8w4LpWg3BEe0YfLzNd2fVlTbqPZOKzKbudy+kaXSeR7+I0uLRreHa/JYhkBNSa9Ro40r3m1dCPz5xKePTut0Wx5VPZ7MlYQhEyohCEACEIQAIQhAAj8JAFybAR+xmG0/FpUpygSCuzwmnB9L/AHY/P4dY3CDm6RjJNQjbI/HOL36/M+p6RnVKKXu/Z+9MqvoB9n8ePCLbgbBLFDbROzyUvVNQ48Us9yep6q+GnHz2d4PTRZZNRnm/8SeToD+pSeX3jzPl1vG4sxFO4iqX9mcOHMFXTMzKTpYaEXHBI5nnwHfZu+iHHc50q/UybvsjoxPjWZm531HhdBmJxy6TMIsQnrl5ac1HQd8duE8BStLUJ6qKE9U1HOVL7SUK6i+qj9o+Vol8K4YksNyW6YTnmHNXn1DtLPTuA5CPfFMxOyuHp56nIUucS0d0Ei5v1A5kC58om5/xgVUP5zJHfs+kej71G+y593mGbLe17dL84qWP5+tS0zSpaiv7t+YU4rJYe0KEhQTcjmAdNLxTqbMpdmZacomH6tP1JkBTk5NTKwFKt2gbHKQTyuPCJiszT+LpCgzTdFdm1B93fy2bKjsixBXpYE248dRGlj0tNmXl1RaXJZsKYlksVU1SFpSiaSi0xLq6HQkdUn5cDFTwfiOTwtS6vSqi+EvyMytLKObvKyR4pv8AtRYRgaTOIEVZtxUkhARkl5QBqxA1zKHG/O1r2ifp9EpdNUVychLsrPFaUDN8eMLVBWuzGozbTfKKfV5St1KTw1iRiTD1QlUhb8un2ZIVYmwUdOFrcdecS1Dl6lUMTu16ep5pzSZMSrbK1hS19rMVG3ADhaLVCMOdqqNrGk7sz6n0/FNOxFUqx6mlHnJ5IGRM4AG7W5lNzwHIRL4Nw9O06an6tVnW11GfVdSG9UtJvfKDz5fAcYtUIHkbVBHEk7KjtJxBL0igTMrvgmcm2ihpHPKSAo+QJip1pmsYawUxTXDT5mUnLNoypUHkLV2yOYVzF9DwjVZmWYm2izMsNvNK4ocSFA+Riu1jBVPqD0s/LvTEk9K5NzuSC2jLbLZCgQLWHC17axqE0qTMZMcpW0R8+hnAmB7SrqZecsjtAZw69YZtCbAGxvbgLnjEnT8Srl6bKP4jZbpjsyrKg5iWzoCCT9DjayjxBiIx8xkr9EqNQbdcosqpSnt2gqDauIKgORITr0BHPX2l1NY1ryJndl2gU9J3ZcQcsy8RYnKoapSNNRxh0mrYW1Kl9v8ApYa3Q6biCU3M6ylwW7Dg0UjvSYoH+N7Npn6U/QHF/uXP8Kv4VdxOlmrmOaLQLSrCTMqYshbcsBlZSNLE8AbDQd3KLOpDM7KZXWgtl5HaQ4niCOBEJScV1LYcoxm7i90RX+DYzof0ZmVc8ltLHzSof6uDGWT8jV9n1eS+w5mYVo07bsvp4lCx17vMd07V6XUNn9SNXo+Z6kukJeYUScgv7p7vqq4jgb31uyFUnGmHb/ppSYGo4LaWPwUD/ogxtPRut4snKPmbPaSPXDVelMQ01E5KmyuDrR95tXQ/kecS0YgDUtnmJ7HM40fJMy1+Sh8j3HXZqbPy9TkWZ2UcDjDycyT+IPeDoR1jGTHp3XDKYsmrZ8o6YQhEiwhCEACEI/FqShJUogJHEmACt49xGMPUZSmlJ9NmLoYB5HmrwH4kRTdl2GDOzHr6eSVNNLJl0q1zuX1Wb9Dw77nlEPUHn8eY0S0wpSWFKyNK/wAtlOpVbqdT4kCNSr1SlMJ4bLjSEpSygNS7X1lWskfme4GOlpwioLlnKmsknN8IgNoeI5hDjeHKPmcqM3ZLm74oSeQPIkanoNdL3idwdhmXw1TAwizky5ZTztuJ6DokchEDszoTgQ7iSokuT09dTZXxCDrm7ir8LdYtlaLT0k5JmpJkXXxlS4FALGuuW/O14nJ10L5KQV/qP4Ih/Fjq62qQpdLdqLDJ3cw+26lAQ5xypzWCiBcmx0iyoebcWtCHEqW2QFpBuUm19YyOq0qbwy9J06ovv+oEzJdZnJZCQ4ysgga2uDc3I5205iLbg1uZn61P15C3EU+YbQy1vEgKmcgtviLC17G2moPK0OUEla4FDI26fJ7zuGKpNVaYKcRTzNLmElSmW19tKiRolRBsm1+FrRYaXT5alSDMjJththlOVKfxJ7ydY6oRJybKqKW4hCEI0IQhAAhCEACEIQAIgMW0OdrUs03JVJ2UymzjSVEIeQSLgkag2Gh8dNYn4Q06doTSapmQztMkncWyOGqWp9NPTNb+YlXkEBCkjUhShcgpBte4104xfcZYmaw5IoWnduzjihu5dRN1pB7RFuFhfU6R2Vuk+mJ9Kk90zVWUkS8ypGbJfiD3HUHpe41jLKm0/MVBqmPsTk7VpjK7VVN2cdQnilpFuyhNrEm4GovwtF41kavsc0rxJ13NakJuUrlJbmWhvZSab91aeIOhBB8xGdPtzGzfEiH2947Qp5WVSdTk7vvDiDzFxx1joksZ1RqttyEtS2nJGVRldlZEF5TKBYe8NCR0AtyuTwvlapcvWqW/ITKfZvJ0PNJ5Ed4MZ9Dp8M3+4rjyiNxTRJTFlBTunEKXl30q8nUXI69CND/0ig7NsQO0WsO0WoZm2HncgSs/oXgctu4KOnjbviZ2d1OYo9VmsJVRXtW1lUurl1IHcR2h5xx7W8PBpSK5Kpy7whExl+twSv8AI+Ubgqbxy4fBObtLLHlcmpQit4Cr/r+gNOOrzTbHsn+8jgrzFj43iyRztNOmdUZKStCEIQhiKdtRrHq3DplWlWfnlbodyOKz8NP2ouMYxtBmXa/jZNMll/oVIlWuYzqPaV5E2P3Yrhjqnv2I55aYbcstGyOi+i0p2rOj2k4crfc2D+Zv5ARwV3NjTHjdHSrNTKeDv8vAkEZ/ibI7tTFzrc2zhjCrrjCQlEowGmE/asEoHxtEHsopHoVBVUHbqfn1leZXHICQPibnzjWrnJ9jOn04/uWatVOXoVJdnHEkoaSEttp4rVwSkd5NhGfYdpNAxmw+/Up116uPFSnU5ygtC+iUJOhSBYc/KNSioYxwcxUml1CmNmXrTZC2nWl7vOq/0j17+PfGMcktuP7N5It78r2ODBlPVUKVV8PVVxc3JyM4GkLzkZgkg5b34Agacr25RfEIS2hKEJSlCRYJSLACI/D1IaolLak21FxYut11XFxw6qUfExJQpytmoR0rcQiMk8QUmdqT1Olp5pycZJC2gbG44262524R3TL3o8s69u1ubtBVkbF1KsL2A5mM0zSafB6wjL8b499IpjUrR3JqUmlqPpCVoU060ANE9xJPEHl3xHYAxZWfXsnTn5l6dln1FBS6rMpPZJzBR7WluBNrXivkS06iL8RFTUTYYQhES4hCEACEIQAIQhAAit42o07UqU6qlzbktNpBuErypeSRYpV5cDy15ExZIQ06doUo6lTKTQq3gvDdLbYlKlLgKSFLUklxazbiqwv5WFugiYouLqTWp9yRk3Hd+hGfK42UXGnC/iIqmOG5TDzTcrTqY6JycmfSpWabt2H8wukDjax0TwN7dYseCsOeo5NyanVbyqTftJl1Rvbnlv3czzPlFZKOnU+5GDlq07UiH2pUh0My2IZEZZuRUnOpPHLe4PfY/ImLHIzEpi7CyVrSN1OMlDieaFcCPEHge4GJJQlKrT1AKbmJSZbIulV0rSRyIig7NX3aPW6thmaUczSy41fnawJ/aSUK+MJPVD+0NrTP+mV/Ac4/hrGi6XOKypfWZV3pnB7CvM6DuVGzxkm12lmUrEtVWbp9KTlUocnEWsfMW/djSsOVIVihyVQFsz7QKwOS+Ch5KBEazdSU13M4OlvG+xIwhCIHQeM5MIlJR+Zc/RstqcV4AXMZBswllVXGDtRf7S2UrmFq/wB4s2/4lHyjQdok16Jg6oqHFxAaH7RAPyJiv7GpQIplRnLWLj4aHgkX/FcXhtjkznydWWMfkbWZh2acpFCl1e0m3syh5hCb911E+UXtCZel01KB7OWlGbfdQkf0EUBZ9b7YUp95unNfgm/8znyi44rkpyo0CbkZHIHpkBoqWbBKSQFHv7N9IzLZRj+bmoO3KX5sVT+0uNJ1j1nTqEx6tUM7aXNXVo5HRQOo6J8L8YtuGK4ziGkNVBlBbKrpW2TfIocRfn18CIqaVY6w3LIRupKqyMum3ZshSUAafV4AdFRObPWFow03NOpCXZ51ybUkcBnUSLd1rQ5pVaoWNvVTv5LLCEIiXMKxlSZ7DGJVTTTriUuOqmZV5PebkeIJsRzBHW0aZgrF8viKWDTuVmoNjttX0WPrJ7uo5fAmWxFRZWv0t2RmRYK1QscW1ciP9ai4jB5+UqGHayph1SpeclVZkLbVbwUk8wR+YPMR1xrNGnyjileCVr0s78eszMvi2p+k5szjudtSvpII7NuoAFv2SI69nlMq87VXZqlPNS7sqg+1dazoUVWGQ9CRc3GoA74tWHsV0bE6WKfiSUlfTBo046gZHSehPuk9OB5dI0CSk5WRl0sSku1Lsp4IbQEgeQgnlcY6Gtx48KlLWnsfsl6T6Iz6ZuvSsg3u6vkz21y31tfrHtCEch2CEIQAI5p2fkpBAXOTbEshRsFPOBAJ846YwraO/MPYwnkzOb2OVLSVcAjKCLdxJJ8bxTFj8yVEs2Ty43RuLDzUw0l1h1DrSxdK0KCkkdxEVrG2K/7O+hMsoQ5MTDoulV7JbBGY6czew8+kVbY9NPtetUuqyyLaEuqJ91Ctbnuuka/dEV+bm3cY46ZU1m3Tz6W2h0ZSbk92mY+JtFI4UptPhEp524Jrlm5QhCOc6iIxUw67RX3ZZttc5LDfy5WgKyrTqCAedrjzioyMvi/F8m1NvVdinU59OZIlL51JPgbjzV5RosZrLVfD2C6pOy3ptYSWXVD0FWVTZzAKCkiwAGulyD1iuNuqS3I5UrTb2LnhWju0KkIpzkz6QhpxZaVlsQgkkA9+pim44HqLHdGrqey09ZD3TTskn9lQ/djpbxzUp+pZZGkvNMOSy1S6JlBHpDibKslQ0uUhQABOpENowNawGzUVSj0u424h0tOpstAN0kEftRqCan1d/wDpicoyx9Pb/hK7TZAT2EZpVrrlSH0+Wh/hKoi9j08XqNOSKjf0Z/Mn7qxf+YK+MWWkOCuYRli6b+mSYS54lNlfO8ZxshmVS2JJiTV+uljf7yVA/gVQ4q8covsKTrLGS7mwwhCOc6ii7YHcmGpdvm5NJHwSox27LWd1g6VX/nOOL/iI/KIfbOr/AA2mJ6vqV8E/9YsezxOXBlLHVsn4qJi7/ZX1Odb5n9CtbPbzeN8TTx+i4pCfAuG3yQInsbzEyXqPTpaeXJemTKg66hYQrIlBJAJ4X087RB7I+27XnDxVMJv8Vn84suKMOU+uuyrtTeUmWl0rBQF5AoqtqT3W+cE6WTf82DGm8W35uVep1mou4emJyUFQp7tDO73rj6XkPqBSlSV/XNtcxHHnrGhSef0RjeZc+7TmyiwvbkIzqv4Ao1OlG3GJ6ZZ3z7TSUOrzNrzKAy2Avwv4cTpGlxnJppaTWNSTeoQhCJFhGYbaGWwukv5faK3iCeoGUgfEn4mNPjL9tK7u0drueV/KIrg/cRHxH7bM0Ii6YR2gTtIyytRzzsinQKzXdbHcT7w7j5HlFLjTMG4RpGIcINOzLSm5reOJ37SsqtFG1xwOnUR25nFR6kcOFTcuhmhUqqyNXlRMSEyh5vnlOqT0I4g9xjtjFa/hWs4Ne9aSU4VMJUEpmGbpWi50C08CCdOYPMRdvXTuK8BTyqfb1luCh1ls6pVzA8Re3w4gxxyxJU4vY7YZW7jJUyyylapc7MqlpWoyj76b3bbdSpQtx0BjtWtLaCtaglIFySbAR/PWGpSdfxDItSLa/SW30qOVJBaCVC5V0AF738OcXTahiBVQnGsN05W89olL+Xgtwnso8jYnvt0MalgqSimZj4i4OTRf3MSUJr36zTknoZlF/wAYqmK6/gafShc8E1F5v3NwlWa3TOLC3deOOZ2TNZP7rV3Eq/3zIUPkRFUxZg9/DEtLuzE61Mb9ZQlKEFOWwvfUw4Qxtqpbmck8qTuKo861if0uR9VUyRbplKzXLTarqcPVSufLTu4mLfsgogSy/Wnk9pV2WfAe8rzOnkYy+N52et7rBtMHVsr/AHlE/nFc/RCkS8Pc8mqXYsUIQjhPQEUjEFdpGGMVuPTVNW49Ny6F79vKtRIJSEhJtbQcb66dIu8U/FaajJYikqrKSM1MS4lXZd9cqApxrMQUqSk+8QdbWI0jcKvcxkutjiRtEROzcizJ0yabQ9NIZW8+gZLFViAQeP8AQxY8aMek4Uqrf/p1KHkL/lFcm8MVBpuRkqY5MzMsqbROuvTriQGylWYgJSAcyiok6W05RcK2nPRp9H1pdwfwmNy0ppxMR1NNSK/ste3uDJRP+U46j+MkfIiKJh0+gbVCyPdM2+35HPb8ot+x5ebCrv2ZtQ/hQfzipPey2taf+YJ+YF/xikfVNfUjLeGN/Q2aEIRynYZ3tmT/AIZTV9H1D4oP9IsWz1WfBlM7m1D4KUIidr7O8wu07/kzSVfFKh+JEdOyt/e4OYR/kuuN/wARP/FF3vhX1OdbZ39CJ2SdiZr7J95D6b/FY/KOvaDLSM7XKDK1aZDFMVv1OqLgbTmCRluTpzI8++OLAI9Cx5iWSvbeOLcSO4OEj5LEW+vYdka89Jqn0qcbllKVu72C8wtrbXofKCUksl/nAQi3j0/nJl9NepTS/SKzV1TcjSX1NSEm2u6lpSvRfIWtY8dQLcBY7RFcfwNht6VcYFLZb3ibbxA7Y8FG5EWOM5JqXBvFBwuxCEIkVEZLtkczVmntfVl1K+Kv/wCY1qMb2vLvippPSTR/MuL+HXWc/iXWNlIjZNkLmfCzqf8ALm1p+ST+cUyv0dprAFAqLTLaXcykulIsVBdyCTztlA84sWxiYzSdTlvquId+KbH+WL5nrxtrsc+BaMiT7o0OblmZyWdlpltLrLqSlaFcFA8oxfENGquBqx6VTpl1uWcuGH09OORY4EjvFja/W22xSdrpthRA6zSB8lRz4ZNSrszqzwTjfdFBmtoGJJmWUwZ1Ld+yVstJSo/tcvEWiybM8IuKdZr8/qj35VCuJv8ArD+Xx6Rmkf0LhL/srRv/AILH8gi+fojUVVnL4f8AUncndEtGX7ZpxKnqZIIPtEpW6vuBsB8bK+EaHV6pKUeQcnZ10NstjzUeQA5kxgFdqr9aqszUX/eeV2U8kJGgSPAfE3POJeGg3LV7FvFZEo6fc4I3nZ7MtTOD6bujfdN7pQ6KSSD+F/OMGi+bKcQGSqaqU+r2E4q6Psu2/wCIC3iBHR4iGqG3Y5/DT0z37mvwhCPPPSEUvFjbtSxPJ04VKbkJRmTcmppbD6m8yMwAGmnI6ngIukQeJcK03EYaM6HkONAhLjS8qrHiDodI3BpPcxNNrYo1NrddmX2a96wcRKPVFEnLyB1DjZIB8wOfG4OvKNHri8lEqC/qyzh/hMRjWDaQ1NSMwhL49ASBLo3pyoIJJVbqSdTzj1xu+JfCVVX9ZhTY8Vdn841KSlJUYjGUIvUQWx5GTCrp+tNLP8KB+UVJw73a3p/+eP4QL/hF82YMFnBkkT7zinFn98gfICKDhgesNqO/Hu+mTLvkM9vxEVj6pv6kZenGvobRCEI5TsK9tAlfS8H1NI4ttb79whR+QMVnYzN5pOpyZN926l1PgU2P8vzjQ5hlEww4y4LocSUKHUEWMY5s4fXRcbrpz6v0m8lV/fSbg/FJA8YvDqxyXyc+Tpyxl8E/Nn1RtfYdIs1UGgCe8pKbfvIT8Y0iM92uSjjUvTK1Liz8k/lzdLkFJPgpI+MXqnTbdQkJacZN2320uJ8CLxme8Yy+DWPaUo/P3OiEIRIsIQhAAjH9sKcuJJVf15RKfgpf9Y2CM32v0iZmvV89KsOvZczC0toKzqQU6DXjceJEW8O0pqyHiIt43R2zkh6ZskYaSO03ItPp8UgKPyvFY2QTW6xJMMH/ALxLH4pII+RMajRpLcYekZB9Orco2ytPggAiM1wlhasUfHjG8lHhKS6nP7xbsLQUqCTfhc3GnERuEk4yTJzhJShJGtxRNsP/AGblv/lp/lVF7ik7XGivCqXeTMyhSvAgj8SIlidTRfMrxsyickky9Mp019KbS4o92VZSPwjesMJyYapKPqybI/gEYtX5dxOG8M5UqzOMP5U9bukj45hG7yjPo8oyz/loSj4C0W8Q7S+Tn8NGm/gqO0LCUziFpuZk5hW/l0nLLrV2HPDklXfz4G3GMbmGHZV51h9tTbrailaFCxBHEGP6XjDqbIevdozrTiczap9111KhpkSsqsfGwHnD8PkaTT4QvE402muWVW8X3BWA6m/PytRqLSpKWZWl1KFaOrKSCNOKRca3se7nH7iPDfpm0VqnSsolmVcS26oNthKA2PfOgtxBHiRGuw8ufZae4sODqersIQhHGdwhCEACKNtenRL4YRKg9qafSnyT2vxA+MXmM1xYfX+0ak0dPaak7Ldt1NlqB8ko/eimJdVvsSzPor32LjJJTQMItBYsJGSBV4pRc/OM52Oyinq9NTi/1Mtb9pah+STFw2pVH0LCrrKTZycWllPhxPyFvOOLZBIFjD8xPKHam3zb7qOz/Nmikdscpe5OSvLGK7F8hCEc50iMb2mSTtHxc1U5bsmYyzCDy3iCAfwSf2jGyRVdpNFNXw06tpGaZk/bt24kD3k+Yv5gRXDLTPclnhqg6JCdaYxVhRaGzZuelwpBP0VEApv4G3wiu7J6op2lv0aZumakFnsK4hJJuPJWYfCOXZDWw7KP0V1XaZu8x3oJ7Q8lG/7UeGK23MIYzlsQy6FehTisswlI5n3x4kAKHUpMb07vH9ietNLL9zTYR8MutvstvNLC23EhSVDgQdQY+45zpEIQgAQhCABCEIAEctTp8tVJF6SnG95LvCyk3I+Y4R1QgAiX8OUmY9XbyTSoU23owubIsBYW58AdegiWhCHYkkhEVTcO0umVKbqMpLBE1NqKnVlROpNza/C510iVhBbQNJiEIQhiEIQAIQhABzz82zIST82+rK0ygrUe4CKHsulX5+cqeJJxNnZpZQjzN1W7h2UjwMfu02qOz0zJ4Wp/amZpxKnegF+yD/MegA6xaCZPCOFf/TyLHgVq/qpR+JiyWmH9sg3qnfaP/pnW1apKqWImKUxdXoqQjKPpOrsbfDKPMxqVEp6aVSJOQRqJdpKCepA1PmbmMq2b096uYrdq012kS5L61clOqJsPLU+QjY4ebpSguwsCcm8j7iEIRA6BCEIAMTxFJP4Ixg3OSacsvn30ungFJOim/AXI8CDGoT0vIYwwzZCs0vNthbS7aoVyNuoOhHiI/MZ4fRiKiuSwypmm/aS6zyWOR7jwP/SM92cYkVQqiqi1PMyw8sgbzTcu3sQe4nQ9DbqY6G/MimuUcteXNxfpZObOKy/ITT+Fat7Oal1HcZjxHEpHdbUdQe6L++3vWVt5lozJIzINlDwMVDaFhd2qNIq1MzJqkpZSchspxINwB9oHUfCOvA2Km8RyG6fs3UWU+2b4ZhwzDu69D5Ria1LWvkpB6X5cvgg6BNzk5h7DM07UpxT85OqQ97Y9tIz6eAyJ+J6xHzVQq0pNuMPVGdVKTVRMvLuJcOZooeCSknmChRPimNClaDSZSeVPMSDDc0oklxKdQTxI6X524x+N4fpLTW6RIMhG9D9rfrBwV498NZFfAvLlXJU5x2dTNY0Sioz2WRYQuXSHT7MlvObeY+FxHpTZ2dkqlhkCpTE0iqyxXMsvrCslmwrONLgXuOkWdzDtHccmnFyDRVN/pzr7TW+vnCVw7RpRLqZemyzYdQW1lKNVJPK/G0LXGh6JX+e5VKBiWamMW5ph2YFNqgWmUS40pLaSg9goURY5ki5sTqQIj3JypStBrlWTWZxMxTam4wwh1wKQtCVJASoEakgnXjF6VhyjqblW1SDJRKfoBr7PW+nnHxL4XoUu+l9qlyqXUqzpVkuQrrrz74euPsLy5VVnPjCYmWsHzk2067LTLbAcSps2KVaaRD0eqikLVN1qpTku0pO7EvNq3pXo2Q6kpGguspPEcNQQRFwn5GVqMqqVnGEPML95CuBiOl8PYfa9ISzT5MZkbp4BIPZ42V8BGYyVUzcou7RWqhMTaajjEJqU6lMjKodZAdNmlFBWbd1wNOlxHPTqnUpKkuVR2cnN/wChksy0yreCZO6S5vU24AHN100NjFtlqVh/1ZMMMMShknDd7KoFKiPrG+vmY/KPSsPysypylsSaX0oyEtEKISeXHQaQ9argzod3ZD0aXfdp1FqLuIphSptI36HXRleUtB7KALZVAnQD6uoiOo0zOTOHaU+7UpwvvVTcuK3xupOYjL+6kH4mLhI4eo8hMmZlKdLsvG/bQixF+NunlH6zQaSxUVVBqny6JtRKi6Ea3PE+J5niYWtD0PYqbtOqn9pE0j1/PBbkiub3oX2Uu73Syb+4L2y34c4Imp2qN4mnX6tMyTlNdcZYaaWEobCE3ClAjtZj1v3RcVUinqqaamZVszyU5Q9btWta0eE9h2j1CYMxN06XedNsylI963DN184etB5bKLN1qoTC6ROOuVMImKaqZmGJJwJN027SQdLW1sNdREiirVFGCpPPPOPT1SdyS7rALziGySSqyRdSkpBvYcbCLeuj09c81PKlGzNNAJQ5bVIHIR4S2G6NKzDcwxTmGnW1FaFJFspPEgQa4+wljku5yYGqrtVw+yqaKvTZZRl5kLBCgtOnaB1uRYnvJjsxJWpegUl2ef1I7LbY4rWeAH59ACYIlKRh5ibnUNMybahvH3BpmtfU9TqYoEo1M7RsSemPocboUmrKhCtM3O33joT0Fh3kUVJuXYJScYqK5JPZtRn5l6YxRUwVTU4SWCfqniq3IHgPs9xiG2qV/wBYT7VDk8yksODe5RfO6dAkdbX+J6iLljjEbWGaNlYKPTHRkl2/q6e9boP6CKfstw4qdnFV+cSpTSFncZjfeOX1WetjfX61+kUg+csvglJcYY/JesF0MUCgsSqgPSF+0fV1WeI8gAPKJ2EI5223bOpJJUhCEIQxCEIAEZ1tOwh6Y2qtSDWZ9tP95aSP0iR9IDqBx6jwjRYRqE3B2jE4KcaZnuzfGSZ5lqj1F3+9JGWXdUf0yRyJ+sB8fGPvGmFZqXnf7R4dKm55s53WkfT6lI5k80/S8eMTtCwQqUW5WqO2rd3zvsN8Wjxzo7r6kcuI04SuA8eNVBLVMqzoTOaJafULB7oDyCvx8dIu1/kx/KOdP/Hk57MmcGYwlMSS+7UUs1Bse1YJ4/aT1T8xz5E2eKTi/BHp0x62ojnodUQrOcpyh1XW44K7+B59Y5sN4+3TvqvEzapKdb0LzicqT976vjwPHSJuCkrgVjNxemf3L/CPlC0uIC0KCkkXBHOPqJFhCEIAI+vJqK6U+iklsTqgA2pxVgnUXN7HW17acbRmxp1WZpWLZCWp6ms27UvdvKdWo5UlQBIBWVJzEnTUkWN41mEbjPT2Jzx6u5msyiUmputP0iTf9VLpKWHvRmLZnCo2CUmwKgk69OESmB22perzjUiiWmJFTCF+mNSYYOe59mbAA2GvdfWLtCG52qEsdOxCEImVEIQgARzVCelqbKOTc48llhsXUpUReJsV03DrX95c3kyoXRLtm6z3noO8xSpOk1vH043UKwpUnSUnM0wkEZh9kHjcfTPl3UjjtapbIlPJT0x3Z8vvVLaRVdyxvJWgy6+0rmo9T1URwHBN7nvu9QnaVg2gI7Ibl2U5GWk+84roOpJ1J8SYVOp0jB9HQkpQy02nKzLt+8s9APmSfExljaKztDxBmV2Wke8rXdSyDyHUn4kjkBpRLXu9ook35ey3kz6pNPqWP8SuzM0spYSoKecHBtHJCO/jbzJ79plJZmTlmpaXbS2y0kIQhPBIHARy0SkylEpzclJthLaBqea1c1E8yY74nkya3twVxY9C35YhCETKiEIQAIQhAAhCEACM3xvs8TMb2oURpKXVXLsqNAvvR0P2eB7uekQjUJuDtGJ44zVMyXCW0GZpZTTq6l1xhtW73yknes20ssHUgfvDvi+1OkUTF1PQ6vdzCFC7Uw0RmT4H8jp1EeOKcG03ESS6tPo88BZMy2NfBQ+kPn0IjM3pTE2AZtTrSlJl1H9Ki62HeXaHI+Nj0MXSjPeDpkG5Y9pq4lh9W4twQtSqYoVOkp13WUqKR90ajxTccyInKFtHolSytzazT5jmHj7O/wB/gPO0c2H9pdNnQlqqJ9Bf+vxaPnxHnp3xOVXDNAxIzv3JdlwuC6ZmXUAo9+YcfO8Zl7ZF8mocXje3sTrbiHUBba0rSeCkm4MfUZuvZ/WaOtTmG6640m9906Sm/ja6VeaYGvY+o+k9RUz7afptt3Ku/wBmTbzTGfLT9LNea16otf7NIhGdN7VWGVZKhRpmXX0SsE/BQSY7W9qWH1cW55P/ANQP4KMJ4p+w/Px+5eIRSlbT8PDgJw+DQ/rHI/tXpCf0EjOOfeyJ/MweVP2B5sa7mgQjNzjvEdS0pGGXLHgtxK1p+ICR84/DRce13/aNTTTmDxbbWAfgjj4FUPymvU6F5yfpTZca1iej0QET062lzk0k5ln9kcPE6RTH8X4hxO8uVwzT1sscDMuWunxPBPhqekS9G2a0SQO8m95Pu3ud7oi/3R+ZMSVYxVQcOM7hTze8bFkyssAVDusNE+doa0r0q2KWprqdIi8N7PpORe9Oq7nrGeUcx3lyhKuuuqj3q+Aj1xbj2QoeeVlMs3UB2SgHsNn7ZHPuGvhFKrONa9iV/wBBpTD0u25olpi6nFj7RHAdbWHUmJvCuzNCMs1XsqlcRKNnsj7xHHwGneYo411ZX8E1K+nCvkr1FoFZx1U11GffWmWvZcwoaEA+62nhp8Bre546/R6VJ0aRRJyLIbaT8VHmSeZjrabQy2ltpCUNpFkpSLADoBH1EZ5HPbsWx4lDfuIQhEyohCEACEIQAIQhAAhCEACEIQAI+VoS4goWkKSoWKVC4MfUIAKTXtm1JqGd2QUqnvK5Ni7RP3eXkRFLew5i/CT6n5HfqavcrklFxJ71Itc+YI742qEWjmktnuQlgg3a2ZkdM2o1SX9nUJNiaymylJu0vzGov5CLNIbTqDMaTCZqUV9trMP4bn5RaKjR6bVE2npGXmOhcQCR58YrU9s0w/MXLCZiUUf8p0kfBV4erFLlULTmjw7JVvFmGZtuxq8jlPJ5wI+SrR6bvDM12slHe77NKinTGydP/dqypP8A7suFfMERwObJp/6NSlFfebUP6wacXaQa8veJoHoGGUa+iUhPfu2x+UfiqzhmQ09YUpg9Eutg/ARnw2T1L/zCT+Cv6R0S2yR/9fWW0jo3LlXzKh+EGnH3kLXk7QLVObQsNSvCeU+r6rTSj8yAPnFcqO1hN8tOpalD68ysJ+Sb/jHdKbKqS2P7zOzj/ckpbHyF/nFhp+DsPU8pUzS2FLHBToLh/ivB+ivdjrNL2RmS6zjPFvs5X0lTCuUsjdNeBX+RMTND2VuqKXKxNpbT/kS2p81EWHkPONSAAFhCB53VRVAvDq7k7OCkUanUaX3NPlG2E8ykdpXieJ8474QiDdnQlQhCEACEIQAIQhAAhCEAH//Z"

# --- ESTILOS SOLO PARA LOGIN DARK ---
st.markdown('''
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
.stApp {
    background: radial-gradient(ellipse at top, #132a4c 0%, #0a1931 60%, #061024 100%) !important;
    font-family: 'Inter', sans-serif;
}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.block-container {
    padding-top: 30px !important;
    max-width: 440px !important;
}
.login-card {
    background: linear-gradient(180deg, #14233f 0%, #0f1e38 100%);
    border-radius: 20px;
    padding: 36px 32px 28px 32px;
    box-shadow: 0 25px 60px rgba(0,0,0,0.5), 0 0 0 1px rgba(255,255,255,0.06) inset;
    border: 1px solid rgba(255,255,255,0.08);
}
.logo-icon {
    width: 68px; height: 68px;
    background: linear-gradient(135deg, #3b82f6, #1e40af);
    border-radius: 16px;
    display: flex; align-items: center; justify-content: center;
    margin: 0 auto 18px auto;
    box-shadow: 0 10px 25px rgba(59,130,246,0.4);
}
.title {
    text-align: center; color: white; font-weight: 800;
    font-size: 22px; line-height: 1.25; margin-bottom: 6px;
}
.subtitle {
    text-align: center; color: #8da2c0; font-size: 12px; margin-bottom: 22px;
}
.label {
    color: #cbd5e1; font-size: 13px; font-weight: 600; margin-bottom: 7px; margin-top: 14px;
}
.stTextInput > div > div > input {
    background: #f1f5f9 !important;
    border-radius: 10px !important;
    border: 1px solid #e2e8f0 !important;
    padding: 13px 14px !important;
    font-size: 14px !important;
    color: #0f172a !important;
}
.stButton > button {
    background: linear-gradient(90deg, #2563eb, #1d9bd6) !important;
    color: white !important;
    border-radius: 12px !important;
    padding: 14px !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    border: none !important;
    margin-top: 18px !important;
    box-shadow: 0 10px 25px rgba(37,99,235,0.35) !important;
}
.divider {
    height: 1px; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.12), transparent);
    margin: 20px 0 14px 0;
}
.help {
    text-align: center; color: #7c8db0; font-size: 12px; margin-top: 8px;
}
.help a {
    color: #38bdf8; text-decoration: none; font-weight: 600; border-bottom: 1px solid #38bdf8; padding-bottom: 2px;
}
</style>
''', unsafe_allow_html=True)

def login_final():
    st.markdown(f'''
    <div class="login-card">
        <div class="logo-icon">
            <img src="data:image/png;base64,{LOGO_B64}" style="width:62px; height:62px; border-radius:12px; background:white; padding:4px;">
        </div>
        <div class="title">Sistema NOTIWEB<br>UE 405 Huamalíes</div>
        <div class="subtitle">Red de Salud Huamalíes - Huacaybamba</div>
        <div style="height:2px; background: linear-gradient(90deg, transparent, #3b82f6, transparent); width:120px; margin:0 auto 18px auto; border-radius:2px;"></div>
    ''', unsafe_allow_html=True)
    
    st.markdown('<div class="label">Usuario</div>', unsafe_allow_html=True)
    usuario = st.text_input("usuario", placeholder="admin", label_visibility="collapsed", key="user_final")
    st.markdown('<div class="label">Contraseña</div>', unsafe_allow_html=True)
    clave = st.text_input("clave", type="password", placeholder="••••••••", label_visibility="collapsed", key="pass_final")
    ingresar = st.button("Iniciar sesión  →", use_container_width=True)
    
    if ingresar:
        if (usuario == "admin" and clave == "1234") or (usuario == "licenciada" and clave == "licenciada") or (usuario == "huamalies" and clave == "huamalies405"):
            st.session_state['logado'] = True
            st.session_state['usuario'] = usuario
            st.rerun()
        else:
            st.error("❌ Usuario o contraseña incorrecta")
    
    st.markdown('''
        <div class="divider"></div>
        <div class="help">¿Necesitas ayuda?<br><a href="#">Contacta al administrador →</a></div>
        <div style="text-align:center; margin-top:14px; font-size:10px; color:#5a6d8d;">admin/1234 | licenciada/licenciada | UE 405 2026</div>
    </div>
    ''', unsafe_allow_html=True)

if 'logado' not in st.session_state:
    st.session_state['logado'] = False

if not st.session_state['logado']:
    login_final()
    st.stop()

# ================= POST LOGIN - ESTILOS CLAROS =================
st.markdown('''
<style>
.stApp {
    background: #f8fafc !important;
}
.block-container {
    max-width: 100% !important;
    padding-top: 20px !important;
}
[data-testid="stSidebar"] {
    background: white !important;
}
.stTextInput > div > div > input {
    background: white !important;
    color: #0f172a !important;
    border: 1px solid #cbd5e1 !important;
}
</style>
''', unsafe_allow_html=True)

usuario_actual = st.session_state.get('usuario','')

# SIDEBAR ORDENADO: LOGO ARRIBA, MODULOS EN MEDIO, CERRAR SESION AL PIE
with st.sidebar:
    st.markdown(f'''
    <div style="text-align:center; background:white; padding:16px 12px; border-radius:16px; border:1px solid #e2e8f0; box-shadow:0 2px 8px rgba(0,0,0,0.04); margin-bottom:16px;">
        <img src="data:image/png;base64,{LOGO_B64}" style="width:78px; height:78px; border-radius:14px; background:white; padding:4px; border:2px solid #e2e8f0; margin-bottom:8px;">
        <div style="font-weight:800; color:#0f172a; font-size:13px;">UE 405</div>
        <div style="font-size:11px; color:#64748b; margin-top:2px;">{usuario_actual}</div>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown("### 📋 MÓDULOS NOTIWEB")
    modulo = st.selectbox("Selecciona módulo:", ["DIABETES","TUBERCULOSIS","VIOLENCIA FAMILIAR","PLAGUICIDAS","LESIONES DE TRANSITO","MUERTE PERINATAL"], key="modulo_principal")
    
    st.markdown('<div style="height:18px;"></div>', unsafe_allow_html=True)
    
    # CERRAR SESION JUSTO ABAJO DE MODULOS - SIN DESLIZAMIENTO - VISIBLE
    if st.button("Cerrar sesión", use_container_width=True, type="primary"):
        st.session_state['logado'] = False
        st.rerun()
    
    st.markdown('<div style="text-align:center; font-size:10px; color:#94a3b8; margin-top:10px;">UE 405 - 2026</div>', unsafe_allow_html=True)

# HEADER PRINCIPAL
st.markdown(f'''
<div style="display:flex; align-items:center; background:white; padding:12px 18px; border-radius:14px; margin-bottom:16px; border:1px solid #e2e8f0; box-shadow:0 2px 10px rgba(0,0,0,0.05);">
    <img src="data:image/png;base64,{LOGO_B64}" style="width:48px; height:48px; border-radius:12px; background:white; padding:3px; margin-right:12px; border:1px solid #e2e8f0;">
    <div><div style="font-weight:800; color:#0e5c8a; font-size:14px;">RED DE SALUD HUAMALÍES - UE 405</div><div style="font-size:11px; color:#64748b;">NOTIWEB | Usuario: {usuario_actual} | Huacaybamba</div></div>
    <div style="margin-left:auto; background:#f1f5f9; padding:6px 14px; border-radius:20px; font-size:11px; color:#0e5c8a; font-weight:bold;">🏥 2026</div>
</div>
''', unsafe_allow_html=True)

try:
    if modulo == "DIABETES":
        import diabetes
        diabetes.mostrar_pagina()
    elif modulo == "TUBERCULOSIS":
        import tuberculosis
        tuberculosis.mostrar_pagina()
    elif modulo == "VIOLENCIA FAMILIAR":
        import violencia_familiar
        violencia_familiar.mostrar_pagina()
    elif modulo == "PLAGUICIDAS":
        import plaguicidas
        plaguicidas.mostrar_pagina()
    elif modulo == "LESIONES DE TRANSITO":
        import lesiones_transito
        lesiones_transito.mostrar_pagina()
    elif modulo == "MUERTE PERINATAL":
        import muerte_perinatal
        muerte_perinatal.mostrar_pagina()
except Exception as e:
    st.error(f"Error {e}")
    import traceback
    st.code(traceback.format_exc())