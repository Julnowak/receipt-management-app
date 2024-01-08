# Aplikacja do zarządzania paragonami
Projekt będący częścią pracy dyplomowej "Projekt i implementacja aplikacji do zarządzania paragonami".
Nazwa robocza, jaka została nadana aplikacji to "Zebragon". Mimo, iż nie została ona wspomniana w pracy, można się na nią natknąć na głównej stronie aplikacji przed zalogowaniem oraz pod postacią ikony aplikacji mobilnej.

## Wymagania wstępne
- Konieczna jest instalacja poppler oraz pytesseract.
- Python 3.11 oraz biblioteki wyszczególnione w pracy
- Android Studio Flamingo | 2022.2.1

## Sposób uruchamiania
Ze względu na pracę z darmową wersją hostingu ngrok, uzyskanie dostępu do wersji przeglądarkowej oraz aplikacji wymaga kontaktu z twórcą pracy. Aplikacja jednak może działać w środowisku lokalnym z wykorzystanim adresu localhosta oraz polecenia 
**python manage.py runserver** będąc w folderze ZebragonApp. Zalecane jest uprzednie pobranie przygotowanej bazy danych. Zapewnia to dostęp do możliwości przetestowania aplikacji w przeglądarce. Aplikacja jest przystosowana do telefonów i była sprawdzana na urządzeniu o wymiarach ekranu 412x777px, a więc te wymiary są zalecane przy testowaniu aplikacji.
Uruchomienie aplikacji mobilnej w języku Kotlin lokalnie jest nico bardziej skomplikowane i wymaga podmienienia adresu zapewnionego przez hosting ngrok, oznaczonego jako url, adresem, który odpowiada portowi localhost. Należy również pobrać aplikację na telefon z systemem Android poprzez Android Studio.

## Przewodnik po folderach
- **Android_app_folder** - zawiera folder AaMk, w którym znajduje się aplikacja mobilna, utworzona w języku Kotlin, na podstawie dostępnej dokumentacji.
- **Docs** - folder zawierający opis działania aplikacji, ideę projektu oraz źródła wykorzystane przy jej tworzeniu. Schematy tam ukazane w dużym stopniu ukazują sposób działania całej aplikacji.
- **Images** - folder zawierający przykładowe zdjęcia paragonów, wykorzystywanych do tworzenia algorytmu odczytu danych z obrazów.
- **Test_files** - zawiera plik z danymi odczytanymi z paragonów przez człowieka, w celu porównania wyników i zautomatyzowania testów

Pozostałe foldery są folderami odpowiedzialnymi za tworzenie całej struktury aplikacji w całym projekcie. Ich nazwy odpowiadają sekcjom, za które odpowiadają, co zostało szerzej opisane w pracy inżynierskiej.
