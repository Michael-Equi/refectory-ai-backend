import React, {useState, useEffect, useRef} from 'react';
import './styles/styles.css';

const App = () => {

  const [image, setImage] = useState(null);
  const [clicks, setClicks] = useState([]);
  const [isRound, setIsRound] = useState(false);

  const nameRef = useRef();
  const contentRef = useRef();

  useEffect(() => {
    if(image === null){
      fetch('/image').then(res => {
        if(!res.ok){
          throw Error("Error fetching image");
        }
        setImage(res);
      });
    }
  })

  const imageClicked = (event) => {
    setClicks([...clicks, [event.clientX, event.clientY]])
  }

  const sendForm = (e) => {
    e.preventDefault();
    if(clicks.length !== 2){
      alert('Number of clicks should be 2')
    } else {
      const request = {
        method:"POST",
        cache: "no-cache",
        headers:{
          "content_type":"application/json",
        },
        body: JSON.stringify({
          name: nameRef.current.value,
          content: contentRef.current.value,
          points: clicks
        })
      }
      fetch('/addAnnotation', request)
        .then(res => res.blob())
        .then(res => {
          const objectUrl = URL.createObjectURL(res)
        setImage({url: objectUrl});
      });
    }
  }

  /// Contents
  /// image <-
  /// name <- handle in form
  /// round
  /// section

  return (
    <div className="App">
      {
        image !== null ?
          <img src={image.url} alt={''} onClick={imageClicked} style={{margin: 0, padding: 0}}/>
          : null
      }
      <button>Undo</button>
      <button>New Image</button>
      <button>Push to Database</button>
      <button onClick={() => setClicks([])}>Clear clicks</button>
      {
        isRound ?
        <button onClick={() => {setIsRound(false)}}>Rectangle</button> :
        <button onClick={() => {setIsRound(true)}}>Circle</button>
      }
      <br/>
      <form onSubmit={sendForm}>
        <label>
          Points:
          <ul>
              {
                clicks.map((click, idx) => (
                  <li key={idx}>({click[0]}, {click[1]})</li>
                ))
              }
          </ul>
        </label>
        <label>
          Rounded: {isRound ? 'True' : 'False'}
        </label>
        <label>
          Name:
          <input ref={nameRef} type="text" name="name" />
        </label>
        <label>
          Content:
          <input type="text" ref={contentRef} name="content" />
        </label>
        <input type="submit" value="Submit" />
      </form>
    </div>
  );
}

export default App;
