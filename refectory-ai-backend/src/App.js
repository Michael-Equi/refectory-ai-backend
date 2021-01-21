import React, {useState, useEffect, useRef} from 'react';
import './styles/styles.css';

const App = () => {

  const [image, setImage] = useState(null);
  const [clicks, setClicks] = useState([]);
  const [isRound, setIsRound] = useState(false);

  const nameRef = useRef();
  const contentRef = useRef();
  const imgRef = useRef();
  const selectorRef = useRef();

  const update_image = async (res) => {
    if (!res.ok) {
      throw Error('Error getting image');
    }
    const data = await res.blob();
    const objectUrl = URL.createObjectURL(data)
    setImage(objectUrl);
  }

  useEffect(() => {
    if(image === null){
      fetch('/api/image', {cache: "no-store"}).then(update_image);
    }
  })

  const imageClicked = (event) => {
    setClicks([...clicks, [event.pageX - imgRef.current.offsetLeft, event.pageY - imgRef.current.offsetTop]])
  }

  const sendForm = (e) => {
    console.log()
    e.preventDefault();
    if(clicks.length !== 2){
      alert('Number of clicks should be 2')
    } else {
      const request = {
        method:"POST",
        cache: "no-cache",
        headers: {
          "content_type":"application/json",
        },
        body: JSON.stringify({
          name: nameRef.current.value,
          content: contentRef.current.value,
          points: clicks,
          round: isRound,
          section: parseInt(selectorRef.current.value),
        })
      }
      fetch('/api/annotation', request).then(update_image);
      setClicks([])
    }
  }

  return (
    <div className="App">
      {
        image !== null ?
          <img ref={imgRef} src={image} alt={''} onClick={imageClicked} style={{margin: 0, padding: 0}}/>
          : null
      }
      <button onClick={() => fetch('/api/annotation/undo', {method: 'POST', cache: "no-store"}).then(update_image)}>Undo</button>
      <button onClick={() => fetch('/api/annotation/clear', {method: 'POST', cache: "no-store"}).then(update_image)}>Clear</button>
      <button onClick={() => fetch('/api/image', {cache: "no-store"}).then(update_image)}>New Image</button>
      <button onClick={() => fetch('/api/push', {method: 'POST'}).then((res) => res.json())
        .then((data => data.success ? alert('Success') : alert('Failure')))}>
        Push to Database
      </button>
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
        <label>
          Section:
          <select name="Section" ref={selectorRef}>
            <option value="1">Section 1</option>
            <option value="2">Section 2</option>
            <option value="3">Section 3</option>
          </select>
        </label>
        <input type="submit" value="Submit" />
      </form>
    </div>
  );
}

export default App;
